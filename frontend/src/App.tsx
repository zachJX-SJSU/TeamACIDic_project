// frontend/src/App.tsx
import React, { useState } from "react";
import EmployeeProfilePageModern from "./components/EmployeeProfilePageModern";
import LoginPage from "./components/LoginPage";
import DashboardLayout from "./components/DashboardLayout";
import EmployeeSearchPage from "./components/EmployeeSearchPage";
import HRManagementPage from "./components/HRManagementPage";
import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  const { user } = useAuth();
  const [currentPage, setCurrentPage] = useState("profile");

  if (!user) {
    return <LoginPage />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case "profile":
        return <EmployeeProfilePageModern empNo={user.empNo} isManager={user.isManager} />;
      case "search":
        return <EmployeeSearchPage />;
      case "hr-management":
        return user.isHrAdmin ? <HRManagementPage /> : <EmployeeProfilePageModern empNo={user.empNo} isManager={user.isManager} />;
      default:
        return <EmployeeProfilePageModern empNo={user.empNo} isManager={user.isManager} />;
    }
  };

  return (
    <DashboardLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage()}
    </DashboardLayout>
  );
};

export default App;
