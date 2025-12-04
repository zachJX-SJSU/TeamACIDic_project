// frontend/src/App.tsx
import React from "react";
import EmployeeProfilePageModern from "./components/EmployeeProfilePageModern";
import LoginPage from "./components/LoginPage";
import DashboardLayout from "./components/DashboardLayout";
import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <LoginPage />;
  }

  return (
    <DashboardLayout>
      <EmployeeProfilePageModern empNo={user.empNo} isManager={user.isManager} />
    </DashboardLayout>
  );
};

export default App;
