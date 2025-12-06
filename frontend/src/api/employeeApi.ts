// New file - wrapper for employee management endpoints
// Uses existing backend APIs without modifying hrApi.ts
import { api } from "./client";

export interface EmployeeSearchResult {
  emp_no: number;
  first_name: string;
  last_name: string;
  gender: string;
}

export interface EmployeeCreatePayload {
  birth_date: string;
  first_name: string;
  last_name: string;
  gender: "M" | "F";
  hire_date: string;
  dept_no: string;
  title: string;
  starting_salary: number;
}

export interface EmployeeUpdatePayload {
  birth_date?: string;
  first_name?: string;
  last_name?: string;
  gender?: "M" | "F";
  hire_date?: string;
}

export interface Employee {
  emp_no: number;
  first_name: string;
  last_name: string;
  gender: "M" | "F";
  birth_date: string;
  hire_date: string;
}

// Search employees by name
export async function searchEmployeesByName(
  firstName: string = "",
  lastName: string = "",
  page: number = 1
): Promise<EmployeeSearchResult[]> {
  const res = await api.get<EmployeeSearchResult[]>("/employees/search-by-name", {
    params: { first_name: firstName, last_name: lastName, page }
  });
  return res.data;
}

// Get all employees with pagination
export async function getAllEmployees(
  limit: number = 50,
  offset: number = 0
): Promise<Employee[]> {
  const res = await api.get<Employee[]>("/employees", {
    params: { limit, offset }
  });
  return res.data;
}

// Create new employee (HR only)
export async function createNewEmployee(payload: EmployeeCreatePayload): Promise<Employee> {
  const res = await api.post<Employee>("/employees", payload);
  return res.data;
}

// Update employee (HR only)
export async function updateEmployeeInfo(
  empNo: number,
  payload: EmployeeUpdatePayload
): Promise<Employee> {
  const res = await api.put<Employee>(`/employees/${empNo}`, payload);
  return res.data;
}

// Delete employee (HR only - currently disabled per requirements)
export async function deleteEmployeeRecord(empNo: number): Promise<void> {
  await api.delete(`/employees/${empNo}`);
}
