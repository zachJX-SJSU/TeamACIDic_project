from datetime import date, datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from .db import Base


class Employee(Base):
    __tablename__ = "employees"

    emp_no = Column(Integer, primary_key=True, index=True)
    birth_date = Column(Date, nullable=False)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(Enum("M", "F", name="gender_enum"), nullable=False)
    hire_date = Column(Date, nullable=False)

    # Relationships
    leave_requests = relationship(
        "EmployeeLeaveRequest",
        back_populates="employee",
        foreign_keys="EmployeeLeaveRequest.emp_no",
        cascade="all, delete-orphan",
    )
    managed_leave_requests = relationship(
        "EmployeeLeaveRequest",
        back_populates="manager",
        foreign_keys="EmployeeLeaveRequest.manager_emp_no",
    )
    leave_quotas = relationship(
        "EmployeeLeaveQuota",
        back_populates="employee",
        cascade="all, delete-orphan",
    )


class Department(Base):
    __tablename__ = "departments"

    dept_no = Column(String(4), primary_key=True, index=True)
    dept_name = Column(String(40), nullable=False, unique=True)


class EmployeeLeaveRequest(Base):
    __tablename__ = "employee_leave_requests"

    leave_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    emp_no = Column(Integer, ForeignKey("employees.emp_no", ondelete="CASCADE"), nullable=False)
    leave_type_id = Column(SmallInteger, nullable=False)  # 0=paid, 1=unpaid, 2=sick
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_requested = Column(Integer, nullable=False)
    # NOTE: use UPPERCASE values to align with existing MySQL ENUM definition
    # in the employees_dev.sql seed data.
    status = Column(
        Enum("PENDING", "APPROVED", "REJECTED", "CANCELLED", name="leave_status_enum"),
        nullable=False,
        default="PENDING",
    )
    requested_at = Column(DateTime, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    manager_emp_no = Column(Integer, ForeignKey("employees.emp_no", ondelete="SET NULL"), nullable=True)
    employee_comment = Column(String(255), nullable=True)
    manager_comment = Column(String(255), nullable=True)

    employee = relationship("Employee", back_populates="leave_requests", foreign_keys=[emp_no])
    manager = relationship("Employee", back_populates="managed_leave_requests", foreign_keys=[manager_emp_no])


class EmployeeLeaveQuota(Base):
    __tablename__ = "employee_leave_quota"
    
    emp_no = Column(Integer, ForeignKey("employees.emp_no", ondelete="CASCADE"), primary_key=True)
    year = Column(Integer, primary_key=True)
    leave_type_id = Column(SmallInteger, primary_key=True)  # 0=paid, 2=sick
    annual_quota_days = Column(Integer, nullable=False)

    employee = relationship("Employee", back_populates="leave_quotas")

class AuthUser(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_no = Column(Integer, ForeignKey("employees.emp_no", ondelete="CASCADE"), nullable=False)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(SmallInteger, nullable=False, default=1)

    # Link back to Employee (optional but convenient)
    employee = relationship("Employee")