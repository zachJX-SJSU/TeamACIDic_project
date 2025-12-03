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
  empNo: number;      // logged-in employee's emp_no
  isManager: boolean; // derived from auth/roles in real app
}

const EmployeeProfilePage: React.FC<EmployeeProfilePageProps> = ({
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

  useEffect(() => {
    loadMyLeaves();
  }, [empNo]);

  useEffect(() => {
    if (isManager) {
      loadTeamLeaves();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [empNo, isManager]);

  const handleCreateLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!newLeaveStart || !newLeaveEnd) {
      setError("Please provide start and end dates for the leave.");
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
      setNewLeaveComment("");
      setNewLeaveStart("");
      setNewLeaveEnd("");
      await loadMyLeaves();
    } catch (err) {
      console.error(err);
      setError("Failed to create leave request.");
    }
  };

  const handleManagerDecision = async (
    leaveId: number,
    status: Exclude<LeaveStatus, "PENDING">
  ) => {
    setError(null);
    try {
      await updateLeaveRequest(leaveId, {
        status,
        manager_emp_no: empNo,
        manager_comment: managerActionComment || undefined
      });
      setManagerActionComment("");
      await loadTeamLeaves();
    } catch (err: any) {
      console.error(err);
      setError(
        err?.response?.data?.detail ??
          "Failed to update leave request. You may not have permission."
      );
    }
  };

  return (
    <div style={{ padding: "1.5rem", maxWidth: 1000, margin: "0 auto" }}>
      <h1>Employee Profile</h1>

      {error && (
        <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>
      )}

      {/* Basic info */}
      <section
        style={{
          border: "1px solid #ccc",
          padding: "1rem",
          marginBottom: "1rem"
        }}
      >
        <h2>Basic Information</h2>
        {loadingEmployee && <p>Loading profile...</p>}
        {employee && (
          <div>
            <p>
              <strong>Employee No:</strong> {employee.emp_no}
            </p>
            <p>
              <strong>Name:</strong> {employee.first_name}{" "}
              {employee.last_name}
            </p>
            <p>
              <strong>Gender:</strong> {employee.gender}
            </p>
            <p>
              <strong>Birth Date:</strong> {employee.birth_date}
            </p>
            <p>
              <strong>Hire Date:</strong> {employee.hire_date}
            </p>
          </div>
        )}
      </section>

      {/* Salary history */}
      <section
        style={{
          border: "1px solid #ccc",
          padding: "1rem",
          marginBottom: "1rem"
        }}
      >
        <h2>Salary History</h2>
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            alignItems: "center",
            marginBottom: "0.5rem"
          }}
        >
          <label>
            From:
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              style={{ marginLeft: "0.25rem" }}
            />
          </label>
          <label>
            To:
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              style={{ marginLeft: "0.25rem" }}
            />
          </label>
          <button onClick={loadSalaries} disabled={loadingSalaries}>
            {loadingSalaries ? "Loading..." : "Load"}
          </button>
        </div>

        {salaries.length === 0 && !loadingSalaries && (
          <p>No salary records found.</p>
        )}
        {salaries.length > 0 && (
          <table
            style={{ width: "100%", borderCollapse: "collapse" }}
          >
            <thead>
              <tr>
                <th
                  style={{
                    borderBottom: "1px solid #ccc",
                    textAlign: "left"
                  }}
                >
                  From
                </th>
                <th
                  style={{
                    borderBottom: "1px solid #ccc",
                    textAlign: "left"
                  }}
                >
                  To
                </th>
                <th
                  style={{
                    borderBottom: "1px solid #ccc",
                    textAlign: "right"
                  }}
                >
                  Salary
                </th>
              </tr>
            </thead>
            <tbody>
              {salaries.map((s) => (
                <tr key={`${s.emp_no}-${s.from_date}`}>
                  <td>{s.from_date}</td>
                  <td>{s.to_date}</td>
                  <td style={{ textAlign: "right" }}>
                    ${s.salary.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* My leave requests */}
      <section
        style={{
          border: "1px solid #ccc",
          padding: "1rem",
          marginBottom: "1rem"
        }}
      >
        <h2>My Leave Requests</h2>
        {loadingLeaves && <p>Loading leave requests...</p>}
        {myLeaves.length === 0 && !loadingLeaves && (
          <p>No leave requests yet.</p>
        )}
        {myLeaves.length > 0 && (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginBottom: "1rem"
            }}
          >
            <thead>
              <tr>
                <th style={{ borderBottom: "1px solid #ccc" }}>ID</th>
                <th style={{ borderBottom: "1px solid #ccc" }}>Type</th>
                <th style={{ borderBottom: "1px solid #ccc" }}>Start</th>
                <th style={{ borderBottom: "1px solid #ccc" }}>End</th>
                <th style={{ borderBottom: "1px solid #ccc" }}>Status</th>
                <th style={{ borderBottom: "1px solid #ccc" }}>Manager</th>
              </tr>
            </thead>
            <tbody>
              {myLeaves.map((lv) => (
                <tr key={lv.leave_id}>
                  <td>{lv.leave_id}</td>
                  <td>{lv.leave_type_id}</td>
                  <td>{lv.start_date}</td>
                  <td>{lv.end_date}</td>
                  <td>{lv.status}</td>
                  <td>{lv.manager_emp_no ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <h3>Request New Leave</h3>
        <form
          onSubmit={handleCreateLeave}
          style={{
            display: "grid",
            gap: "0.5rem",
            maxWidth: 400
          }}
        >
          <label>
            Leave Type:
            <select
              value={newLeaveTypeId}
              onChange={(e) =>
                setNewLeaveTypeId(Number(e.target.value) as 0 | 1 | 2 | 3)
              }
            >
              <option value={0}>Paid</option>
              <option value={1}>Unpaid</option>
              <option value={2}>Sick Leave</option>
              <option value={3}>Others</option>
            </select>
          </label>
          <label>
            Start Date:
            <input
              type="date"
              value={newLeaveStart}
              onChange={(e) => setNewLeaveStart(e.target.value)}
            />
          </label>
          <label>
            End Date:
            <input
              type="date"
              value={newLeaveEnd}
              onChange={(e) => setNewLeaveEnd(e.target.value)}
            />
          </label>
          <label>
            Comment (optional):
            <textarea
              value={newLeaveComment}
              onChange={(e) => setNewLeaveComment(e.target.value)}
              rows={3}
            />
          </label>
          <button type="submit">Submit Leave Request</button>
        </form>
      </section>

      {/* Manager-only section */}
      {isManager && (
        <section
          style={{
            border: "1px solid #ccc",
            padding: "1rem",
            marginBottom: "1rem"
          }}
        >
          <h2>Manager: Team Leave Approvals</h2>
          {loadingTeamLeaves && <p>Loading team leave requests...</p>}
          {teamLeaves.length === 0 && !loadingTeamLeaves && (
            <p>No pending leave requests for your team.</p>
          )}
          {teamLeaves.length > 0 && (
            <>
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  marginBottom: "1rem"
                }}
              >
                <thead>
                  <tr>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Leave ID
                    </th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Emp No
                    </th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Type
                    </th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Start
                    </th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>End</th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Status
                    </th>
                    <th style={{ borderBottom: "1px solid #ccc" }}>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {teamLeaves.map((lv) => (
                    <tr key={lv.leave_id}>
                      <td>{lv.leave_id}</td>
                      <td>{lv.emp_no}</td>
                      <td>{lv.leave_type_id}</td>
                      <td>{lv.start_date}</td>
                      <td>{lv.end_date}</td>
                      <td>{lv.status}</td>
                      <td>
                        <button
                          type="button"
                          onClick={() =>
                            handleManagerDecision(lv.leave_id, "APPROVED")
                          }
                          style={{ marginRight: "0.5rem" }}
                        >
                          Approve
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            handleManagerDecision(lv.leave_id, "REJECTED")
                          }
                        >
                          Reject
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div style={{ maxWidth: 400 }}>
                <label>
                  Manager Comment (applies to your next action):
                  <textarea
                    value={managerActionComment}
                    onChange={(e) =>
                      setManagerActionComment(e.target.value)
                    }
                    rows={3}
                  />
                </label>
              </div>
            </>
          )}
        </section>
      )}
    </div>
  );
};

export default EmployeeProfilePage;
