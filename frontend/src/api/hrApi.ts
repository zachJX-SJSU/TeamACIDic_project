import { api } from "./client";
import {
  Employee,
  Salary,
  LeaveRequest,
  CreateLeaveRequestPayload,
  UpdateLeaveRequestPayload
} from "./types";

export async function fetchEmployee(empNo: number): Promise<Employee> {
  const res = await api.get<Employee>(`/employees/${empNo}`);
  return res.data;
}

export async function fetchSalaries(
  empNo: number,
  fromDate?: string,
  toDate?: string
): Promise<Salary[]> {
  const params: Record<string, string | number> = { emp_no: empNo };
  if (fromDate) params.from_date = fromDate;
  if (toDate) params.to_date = toDate;

  const res = await api.get<Salary[]>("/salaries", { params });
  return res.data;
}

export async function fetchMyLeaveRequests(empNo: number): Promise<LeaveRequest[]> {
  const res = await api.get<LeaveRequest[]>("/leave-requests", {
    params: { emp_no: empNo }
  });
  return res.data;
}

export async function createLeaveRequest(
  payload: CreateLeaveRequestPayload
): Promise<LeaveRequest> {
  const res = await api.post<LeaveRequest>("/leave-requests", payload);
  return res.data;
}

export async function fetchManagerPendingLeaveRequests(
  managerEmpNo: number
): Promise<LeaveRequest[]> {
  const res = await api.get<LeaveRequest[]>("/leave-requests", {
    params: { manager_emp_no: managerEmpNo, status: "PENDING" }
  });
  return res.data;
}

export async function updateLeaveRequest(
  leaveId: number,
  payload: UpdateLeaveRequestPayload
): Promise<LeaveRequest> {
  const res = await api.put<LeaveRequest>(`/leave-requests/${leaveId}`, payload);
  return res.data;
}
