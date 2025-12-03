from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ---- Employee ----

class EmployeeBase(BaseModel):
    birth_date: date
    first_name: str = Field(max_length=14)
    last_name: str = Field(max_length=16)
    gender: Literal["M", "F"]
    hire_date: date


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    birth_date: Optional[date] = None
    first_name: Optional[str] = Field(default=None, max_length=14)
    last_name: Optional[str] = Field(default=None, max_length=16)
    gender: Optional[Literal["M", "F"]] = None
    hire_date: Optional[date] = None


class Employee(EmployeeBase):
    emp_no: int

    class Config:
        from_attributes = True


# ---- Department ----

class DepartmentBase(BaseModel):
    dept_name: str = Field(max_length=40)


class DepartmentCreate(DepartmentBase):
    dept_no: str = Field(max_length=4)


class DepartmentUpdate(BaseModel):
    dept_name: Optional[str] = Field(default=None, max_length=40)


class Department(DepartmentBase):
    dept_no: str

    class Config:
        from_attributes = True


# ---- Leave Request ----

class LeaveRequestBase(BaseModel):
    emp_no: int
    leave_type_id: Literal[0, 1, 2, 3]
    start_date: date
    end_date: date
    employee_comment: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(BaseModel):
    leave_type_id: Optional[Literal[0, 1, 2, 3]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[Literal["PENDING", "APPROVED", "REJECTED", "CANCELLED"]] = None
    manager_emp_no: Optional[int] = None
    employee_comment: Optional[str] = None
    manager_comment: Optional[str] = None


class LeaveRequest(LeaveRequestBase):
    leave_id: int
    days_requested: int
    status: Literal["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
    requested_at: datetime
    decided_at: Optional[datetime] = None
    manager_emp_no: Optional[int] = None
    manager_comment: Optional[str] = None

    class Config:
        from_attributes = True


# ---- Leave Quota ----

class LeaveQuotaBase(BaseModel):
    emp_no: int
    year: int
    leave_type_id: Literal[2]
    annual_quota_days: int


class LeaveQuotaCreate(LeaveQuotaBase):
    pass


class LeaveQuotaUpdate(BaseModel):
    annual_quota_days: Optional[int] = None


class LeaveQuota(LeaveQuotaBase):
    class Config:
        from_attributes = True


# ---- Auth / Login ----

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    emp_no: int
    message: str = "login successful"

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str
