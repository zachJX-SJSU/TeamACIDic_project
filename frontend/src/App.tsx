import React from "react";
import EmployeeProfilePage from "./components/EmployeeProfilePage";

// For now we hardcode empNo and isManager.
// Later this should come from your auth/JWT.
const App: React.FC = () => {
  const demoEmpNo = 110022; // change to a real emp_no that exists in your DB
  const demoIsManager = true; // flip true/false to test both views

  return (
    <div style={{ fontFamily: "system-ui, sans-serif" }}>
      <EmployeeProfilePage empNo={demoEmpNo} isManager={demoIsManager} />
    </div>
  );
};

export default App;
