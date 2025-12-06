import React, { useEffect, useState } from "react";
import {
  Employee,
  Salary,
  LeaveRequest,
  CreateLeaveRequestPayload,
  LeaveStatus
} from "../api/types";
import {
  fetchEmployee,
  fetchSalaries,
  fetchMyLeaveRequests,
  createLeaveRequest,
  fetchManagerPendingLeaveRequests,
  updateLeaveRequest
} from "../api/hrApi";

interface EmployeeProfilePageProps {
  empNo: number;
  isManager: boolean;
}

const EmployeeProfilePageModern: React.FC<EmployeeProfilePageProps> = ({
  empNo,
  isManager
}) => {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loadingEmployee, setLoadingEmployee] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Salary range
  const [fromDate, setFromDate] = useState<string>("");
  const [toDate, setToDate] = useState<string>("");
  const [salaries, setSalaries] = useState<Salary[]>([]);
  const [loadingSalaries, setLoadingSalaries] = useState(false);

  // My leave requests
  const [myLeaves, setMyLeaves] = useState<LeaveRequest[]>([]);
  const [loadingLeaves, setLoadingLeaves] = useState(false);

  // New leave form
  const [newLeaveTypeId, setNewLeaveTypeId] = useState<0 | 1 | 2 | 3>(0);
  const [newLeaveStart, setNewLeaveStart] = useState<string>("");
  const [newLeaveEnd, setNewLeaveEnd] = useState<string>("");
  const [newLeaveComment, setNewLeaveComment] = useState<string>("");

  // Manager pending requests
  const [teamLeaves, setTeamLeaves] = useState<LeaveRequest[]>([]);
  const [loadingTeamLeaves, setLoadingTeamLeaves] = useState(false);
  const [managerActionComment, setManagerActionComment] = useState<string>("");

  useEffect(() => {
    const loadEmployee = async () => {
      try {
        setLoadingEmployee(true);
        const data = await fetchEmployee(empNo);
        setEmployee(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load employee profile.");
      } finally {
        setLoadingEmployee(false);
      }
    };

    loadEmployee();
  }, [empNo]);

  const loadSalaries = async () => {
    try {
      setLoadingSalaries(true);
      const data = await fetchSalaries(empNo, fromDate || undefined, toDate || undefined);
      setSalaries(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load salaries.");
    } finally {
      setLoadingSalaries(false);
    }
  };

  const loadMyLeaves = async () => {
    try {
      setLoadingLeaves(true);
      const data = await fetchMyLeaveRequests(empNo);
      setMyLeaves(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load your leave requests.");
    } finally {
      setLoadingLeaves(false);
    }
  };

  const loadTeamLeaves = async () => {
    if (!isManager) return;
    try {
      setLoadingTeamLeaves(true);
      const data = await fetchManagerPendingLeaveRequests(empNo);
      setTeamLeaves(data);
    } catch (err) {
      console.error(err);
      setError("Failed to load team leave requests.");
    } finally {
      setLoadingTeamLeaves(false);
    }
  };

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newLeaveStart || !newLeaveEnd) {
      alert("Please provide start and end dates.");
      return;
    }

    const payload: CreateLeaveRequestPayload = {
      emp_no: empNo,
      leave_type_id: newLeaveTypeId,
      start_date: newLeaveStart,
      end_date: newLeaveEnd,
      employee_comment: newLeaveComment || undefined
    };

    try {
      await createLeaveRequest(payload);
      alert("Leave request submitted!");
      setNewLeaveStart("");
      setNewLeaveEnd("");
      setNewLeaveComment("");
      loadMyLeaves();
    } catch (err: any) {
      console.error("Leave request error:", err);
      const errorMsg = err.response?.data?.detail || err.message || "Failed to create leave request.";
      alert(`Failed to create leave request: ${errorMsg}`);
    }
  };

  const handleManagerDecision = async (leaveId: number, newStatus: LeaveStatus) => {
    try {
      await updateLeaveRequest(leaveId, {
        status: newStatus,
        manager_emp_no: empNo,
        manager_comment: managerActionComment || undefined
      });
      alert(`Leave request ${newStatus.toLowerCase()}!`);
      setManagerActionComment("");
      loadTeamLeaves();
    } catch (err) {
      console.error(err);
      alert("Failed to update leave request.");
    }
  };

  const getLeaveTypeLabel = (typeId: number) => {
    const types = ["Paid Leave", "Unpaid Leave", "Sick Leave", "Other"];
    return types[typeId] || "Unknown";
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "APPROVED":
        return "bg-green-100 text-green-800";
      case "REJECTED":
        return "bg-red-100 text-red-800";
      case "PENDING":
        return "bg-yellow-100 text-yellow-800";
      case "CANCELLED":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Employee Dashboard</h1>
          <p className="text-gray-600 mt-1">Manage your profile, leave requests, and salary information</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Employee Profile Card */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {employee?.first_name?.[0]}{employee?.last_name?.[0]}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {employee?.first_name} {employee?.last_name}
              </h2>
              <p className="text-gray-600">Employee #{empNo}</p>
            </div>
          </div>
          {isManager && (
            <span className="px-4 py-2 bg-purple-100 text-purple-800 rounded-lg font-medium text-sm">
              Manager
            </span>
          )}
        </div>

        {loadingEmployee ? (
          <div className="flex items-center justify-center py-8">
            <svg className="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        ) : employee && (
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <div>
                  <p className="text-sm text-gray-500">Birth Date</p>
                  <p className="font-medium text-gray-900">{employee.birth_date}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <div>
                  <p className="text-sm text-gray-500">Gender</p>
                  <p className="font-medium text-gray-900">{employee.gender === 'M' ? 'Male' : 'Female'}</p>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <div>
                  <p className="text-sm text-gray-500">Hire Date</p>
                  <p className="font-medium text-gray-900">{employee.hire_date}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Salary History Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Salary History</h2>
              <p className="text-sm text-gray-600">View your salary records</p>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="input-field"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="input-field"
            />
          </div>
          <div className="flex items-end">
            <button onClick={loadSalaries} disabled={loadingSalaries} className="btn-primary">
              {loadingSalaries ? "Loading..." : "Load"}
            </button>
          </div>
        </div>

        {salaries.length === 0 && !loadingSalaries ? (
          <div className="text-center py-8 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>No salary records found. Select a date range and click Load.</p>
          </div>
        ) : salaries.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">From Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">To Date</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Salary</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="py-3 px-4 text-sm text-gray-900">{fromDate || '-'}</td>
                  <td className="py-3 px-4 text-sm text-gray-900">{toDate || '-'}</td>
                  <td className="py-3 px-4 text-sm text-gray-900 text-right font-semibold">
                    ${salaries.reduce((sum, s) => sum + s.salary, 0).toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* My Leave Requests Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">My Leave Requests</h2>
              <p className="text-sm text-gray-600">Track and manage your time off</p>
            </div>
          </div>
          <button onClick={loadMyLeaves} className="btn-secondary text-sm">
            {loadingLeaves ? "Loading..." : "Refresh"}
          </button>
        </div>

        {myLeaves.length === 0 && !loadingLeaves ? (
          <div className="text-center py-8 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p>No leave requests yet.</p>
          </div>
        ) : myLeaves.length > 0 && (
          <div className="overflow-x-auto mb-6">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">ID</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Type</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Start Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">End Date</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {myLeaves.map((lv, idx) => (
                  <tr key={lv.leave_id} className={idx % 2 === 0 ? "bg-gray-50" : ""}>
                    <td className="py-3 px-4 text-sm text-gray-900">#{lv.leave_id}</td>
                    <td className="py-3 px-4 text-sm text-gray-900">{getLeaveTypeLabel(lv.leave_type_id)}</td>
                    <td className="py-3 px-4 text-sm text-gray-900">{lv.start_date}</td>
                    <td className="py-3 px-4 text-sm text-gray-900">{lv.end_date}</td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(lv.status)}`}>
                        {lv.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* New Leave Request Form */}
        <div className="border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Request New Leave</h3>
          <form onSubmit={handleCreateLeave} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Leave Type</label>
              <select
                value={newLeaveTypeId}
                onChange={(e) => setNewLeaveTypeId(Number(e.target.value) as 0 | 1 | 2 | 3)}
                className="input-field"
              >
                <option value={0}>Paid Leave</option>
                <option value={1}>Unpaid Leave</option>
                <option value={2}>Sick Leave</option>
                <option value={3}>Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={newLeaveStart}
                onChange={(e) => setNewLeaveStart(e.target.value)}
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={newLeaveEnd}
                onChange={(e) => setNewLeaveEnd(e.target.value)}
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Comment (Optional)</label>
              <textarea
                value={newLeaveComment}
                onChange={(e) => setNewLeaveComment(e.target.value)}
                rows={1}
                className="input-field resize-none"
                placeholder="Add a note..."
              />
            </div>
            <div className="md:col-span-2">
              <button type="submit" className="btn-primary">
                Submit Leave Request
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Manager Section */}
      {isManager && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Team Leave Approvals</h2>
                <p className="text-sm text-gray-600">Review and approve team requests</p>
              </div>
            </div>
            <button onClick={loadTeamLeaves} className="btn-secondary text-sm">
              {loadingTeamLeaves ? "Loading..." : "Refresh"}
            </button>
          </div>

          {teamLeaves.length === 0 && !loadingTeamLeaves ? (
            <div className="text-center py-8 text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>No pending leave requests for your team.</p>
            </div>
          ) : teamLeaves.length > 0 && (
            <>
              <div className="overflow-x-auto mb-6">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Leave ID</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Employee</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Type</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Start</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">End</th>
                      <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                      <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teamLeaves.map((lv, idx) => (
                      <tr key={lv.leave_id} className={idx % 2 === 0 ? "bg-gray-50" : ""}>
                        <td className="py-3 px-4 text-sm text-gray-900">#{lv.leave_id}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">Emp #{lv.emp_no}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{getLeaveTypeLabel(lv.leave_type_id)}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{lv.start_date}</td>
                        <td className="py-3 px-4 text-sm text-gray-900">{lv.end_date}</td>
                        <td className="py-3 px-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(lv.status)}`}>
                            {lv.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right space-x-2">
                          <button
                            onClick={() => handleManagerDecision(lv.leave_id, "APPROVED")}
                            className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleManagerDecision(lv.leave_id, "REJECTED")}
                            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
                          >
                            Reject
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Manager Comment (applies to your next action)
                </label>
                <textarea
                  value={managerActionComment}
                  onChange={(e) => setManagerActionComment(e.target.value)}
                  rows={3}
                  className="input-field"
                  placeholder="Add a comment for the employee..."
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default EmployeeProfilePageModern;
