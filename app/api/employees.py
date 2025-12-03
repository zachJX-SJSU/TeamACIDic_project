import logging

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func    

from app.db import get_db
from app import schemas
from app.crud import employees as crud_employees
from app.models import Employee
from app.schemas import EmployeeSearchResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("", response_model=List[schemas.Employee])
def list_employees(
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    logger.info(f"GET /employees called, limit: {limit}, offset: {offset}")
    try:
        employees = crud_employees.get_employees(db, skip=offset, limit=limit)
        logger.info(
            "GET /employees succeeded",
            extra={"limit": limit, "offset": offset, "returned": len(employees)},
        )
        return employees
    except Exception as e:
        # Log the exception with stack trace
        logger.exception("Error in GET /employees")
        # Let FastAPI/Uvicorn handle the actual response (500)
        raise

@router.get("/search-by-name", response_model=List[EmployeeSearchResult])
def search_employees(
    first_name: str = Query("", description="Prefix of first name"),
    last_name: str = Query("", description="Prefix of last name"),
    page: int = Query(1, ge=1, description="Page number"),
    db: Session = Depends(get_db),
):
    """
    Search employees by first/last name prefix.
    Direct SQLAlchemy query, no CRUD helper.
    """
    PAGE_SIZE = 10
    offset = (page - 1) * PAGE_SIZE

    query = db.query(Employee)

    if first_name:
        query = query.filter(
            func.lower(Employee.first_name).like(func.lower(first_name) + "%")
        )

    if last_name:
        query = query.filter(
            func.lower(Employee.last_name).like(func.lower(last_name) + "%")
        )

    employees = (
        query
        .order_by(Employee.first_name, Employee.last_name, Employee.emp_no)
        .limit(PAGE_SIZE)
        .offset(offset)
        .all()
    )
    return employees

@router.post("", response_model=schemas.Employee, status_code=201)
def create_employee(
    employee_in: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
):
    logger.info(f"POST /employees called, employee_in: {employee_in}")
    try:
        employees = crud_employees.create_employee(db, employee_in)
        logger.info("POST /employees succeeded")
        return employees
    except Exception as e:
        # Log the exception with stack trace
        logger.exception("Error in POST /employees")
        # Let FastAPI/Uvicorn handle the actual response (500)
        raise


@router.get("/{emp_no}", response_model=schemas.Employee)
def get_employee(emp_no: int, db: Session = Depends(get_db)):
    db_employee = crud_employees.get_employee(db, emp_no)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@router.put("/{emp_no}", response_model=schemas.Employee)
def update_employee(
    emp_no: int,
    employee_in: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
):
    db_employee = crud_employees.get_employee(db, emp_no)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud_employees.update_employee(db, db_employee, employee_in)


@router.delete("/{emp_no}", status_code=204)
def delete_employee(emp_no: int, db: Session = Depends(get_db)):
    db_employee = crud_employees.get_employee(db, emp_no)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    crud_employees.delete_employee(db, db_employee)
    return None