// frontend/src/App.tsx
import React from "react";
import EmployeeProfilePage from "./components/EmployeeProfilePage";
import LoginPage from "./components/LoginPage";
import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) {
    return <LoginPage />;
  }

  return (
    <div style={{ fontFamily: "system-ui, sans-serif" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "0.5rem 1rem",
          borderBottom: "1px solid #ddd",
          marginBottom: "1rem",
        }}
      >
        <div>Logged in as emp_no: {user.empNo}{user.isManager ? " (Manager)" : ""}</div>
        <button onClick={logout}>Logout</button>
      </div>
      <EmployeeProfilePage empNo={user.empNo} isManager={user.isManager} />
    </div>
  );
};

export default App;
