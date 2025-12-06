export interface Employee {
  emp_no: number;
  first_name: string;
  last_name: string;
  gender: "M" | "F";
  birth_date: string; // ISO date string
  hire_date: string;  // ISO date string
}

export interface Salary {
  emp_no: number;
  salary: number;
  from_date: string;
  to_date: string;
}

export type LeaveStatus = "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";

export interface LeaveRequest {
  leave_id: number;
  emp_no: number;
  leave_type_id: 0 | 1 | 2 | 3; // 0-paid, 1-unpaid, 2-sick, 3-others
  start_date: string;
  end_date: string;
  requested_at: string;
  decided_at: string | null;
  status: LeaveStatus;
  manager_emp_no: number | null;
  employee_comment: string | null;
  manager_comment: string | null;
}

export interface CreateLeaveRequestPayload {
  emp_no: number;
  leave_type_id: 0 | 1 | 2 | 3;
  start_date: string;
  end_date: string;
  employee_comment?: string;
}

export interface UpdateLeaveRequestPayload {
  status: LeaveStatus;
  manager_emp_no: number;
  manager_comment?: string;
}

export interface SalaryPeriod {
  salary: number;
  start_date: string;
  end_date: string;
}