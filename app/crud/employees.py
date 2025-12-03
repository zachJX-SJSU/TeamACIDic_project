from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.security import hash_password
from datetime import date

def get_employee(db: Session, emp_no: int) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.emp_no == emp_no).first()


def get_employees(db: Session, skip: int = 0, limit: int = 50) -> List[models.Employee]:
    return (
        db.query(models.Employee)
        .order_by(models.Employee.emp_no)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_employee(db: Session, employee_in: schemas.EmployeeCreate) -> models.Employee:
    # 1. Create the Employee row
    employee = models.Employee(**employee_in.model_dump())
    db.add(employee)
    db.flush()  # get employee.emp_no without committing yet

    # 2. Create matching AuthUser row with initials_empNo and default password "abc123"
    initials = (employee.first_name[0] + employee.last_name[0]).lower()
    username = f"{initials}_{employee.emp_no}"

    auth_user = models.AuthUser(
        emp_no=employee.emp_no,
        username=username,
        password_hash=hash_password("abc123"),
        is_active=1,
    )
    db.add(auth_user)

    # Common dates
    start_date = employee.hire_date
    far_future = date(9999, 1, 1)

    # 3. Dept assignment (dept_emp)
    db.add(
        models.DeptEmp(
            emp_no=employee.emp_no,
            dept_no=employee_in.dept_no,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # 4. Starting salary (salaries)
    db.add(
        models.Salary(
            emp_no=employee.emp_no,
            salary=employee_in.starting_salary,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # 5. Starting title (titles)
    db.add(
        models.Title(
            emp_no=employee.emp_no,
            title=employee_in.title,
            from_date=start_date,
            to_date=far_future,
        )
    )

    # 6. Initial leave quota (sick leave, current year)
    hire_year = start_date.year
    db.add(
        models.EmployeeLeaveQuota(
            emp_no=employee.emp_no,
            year=hire_year,
            leave_type_id=2,  # sick_leave
            quota_days=DEFAULT_SICK_LEAVE_DAYS,
            used_days=0,
        )
    )

    # Commit both in a single transaction
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(
    db: Session, db_employee: models.Employee, employee_in: schemas.EmployeeUpdate
) -> models.Employee:
    data = employee_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_employee, key, value)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, db_employee: models.Employee) -> None:
    db.delete(db_employee)
    db.commit()
