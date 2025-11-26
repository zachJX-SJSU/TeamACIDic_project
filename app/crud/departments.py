from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


def get_department(db: Session, dept_no: str) -> Optional[models.Department]:
    return db.query(models.Department).filter(models.Department.dept_no == dept_no).first()


def get_departments(db: Session) -> List[models.Department]:
    return db.query(models.Department).order_by(models.Department.dept_no).all()


def create_department(db: Session, dept_in: schemas.DepartmentCreate) -> models.Department:
    dept = models.Department(**dept_in.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def update_department(
    db: Session, db_dept: models.Department, dept_in: schemas.DepartmentUpdate
) -> models.Department:
    data = dept_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_dept, key, value)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept


def delete_department(db: Session, db_dept: models.Department) -> None:
    db.delete(db_dept)
    db.commit()
