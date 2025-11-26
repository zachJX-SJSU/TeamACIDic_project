from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import schemas
from app.crud import departments as crud_departments

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=List[schemas.Department])
def list_departments(db: Session = Depends(get_db)):
    return crud_departments.get_departments(db)


@router.post("", response_model=schemas.Department, status_code=201)
def create_department(
    dept_in: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
):
    return crud_departments.create_department(db, dept_in)


@router.get("/{dept_no}", response_model=schemas.Department)
def get_department(dept_no: str, db: Session = Depends(get_db)):
    db_dept = crud_departments.get_department(db, dept_no)
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_dept


@router.put("/{dept_no}", response_model=schemas.Department)
def update_department(
    dept_no: str,
    dept_in: schemas.DepartmentUpdate,
    db: Session = Depends(get_db),
):
    db_dept = crud_departments.get_department(db, dept_no)
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return crud_departments.update_department(db, db_dept, dept_in)


@router.delete("/{dept_no}", status_code=204)
def delete_department(dept_no: str, db: Session = Depends(get_db)):
    db_dept = crud_departments.get_department(db, dept_no)
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    crud_departments.delete_department(db, db_dept)
    return None
