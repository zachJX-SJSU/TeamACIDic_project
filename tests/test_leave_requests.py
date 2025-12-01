from datetime import date, timedelta
from sqlalchemy.orm import Session

from app import models
from tests.conftest import TestingSessionLocal


def create_test_employee(db: Session, emp_no: int, first_name: str = "Test", last_name: str = "Employee") -> models.Employee:
    """Helper to create a test employee"""
    employee = models.Employee(
        emp_no=emp_no,
        birth_date=date(1990, 1, 1),
        first_name=first_name,
        last_name=last_name,
        gender="M",
        hire_date=date(2020, 1, 1),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


# Test Case 1: Create paid leave request with sufficient quota
def test_create_paid_leave_request_sufficient_quota(client):
    """Test creating a paid leave request when employee has sufficient quota (10 days default)"""
    db = TestingSessionLocal()
    try:
        # Create test employee
        employee = create_test_employee(db, emp_no=10001, first_name="John", last_name="Doe")
        
        # Create leave request for 5 days (within 10 day quota)
        payload = {
            "emp_no": 10001,
            "leave_type_id": 0,  # paid
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=11)),  # 5 days inclusive
            "employee_comment": "Vacation request"
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["emp_no"] == 10001
        assert data["leave_type_id"] == 0
        assert data["status"] == "PENDING"
        assert data["days_requested"] == 5
        assert data["employee_comment"] == "Vacation request"
    finally:
        db.close()


# Test Case 2: Create sick leave request with sufficient quota
def test_create_sick_leave_request_sufficient_quota(client):
    """Test creating a sick leave request when employee has sufficient quota (5 days default)"""
    db = TestingSessionLocal()
    try:
        # Create test employee
        employee = create_test_employee(db, emp_no=10002, first_name="Jane", last_name="Smith")
        
        # Create leave request for 3 days (within 5 day quota)
        payload = {
            "emp_no": 10002,
            "leave_type_id": 2,  # sick
            "start_date": str(date.today() + timedelta(days=1)),
            "end_date": str(date.today() + timedelta(days=3)),  # 3 days inclusive
            "employee_comment": "Medical appointment"
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["leave_type_id"] == 2
        assert data["status"] == "PENDING"
        assert data["days_requested"] == 3
    finally:
        db.close()


# Test Case 3: Create leave request with insufficient quota (should fail)
def test_create_leave_request_insufficient_quota(client):
    """Test creating a leave request when quota is insufficient - should return error"""
    db = TestingSessionLocal()
    try:
        # Create test employee
        employee = create_test_employee(db, emp_no=10003, first_name="Bob", last_name="Wilson")
        
        # Try to create leave request for 15 days (exceeds 10 day paid quota)
        payload = {
            "emp_no": 10003,
            "leave_type_id": 0,  # paid
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=21)),  # 15 days inclusive
            "employee_comment": "Long vacation"
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 400
        assert "Insufficient quota" in response.json()["detail"]
    finally:
        db.close()


# Test Case 4: Create unpaid leave request (no quota check)
def test_create_unpaid_leave_request_no_quota_check(client):
    """Test creating an unpaid leave request - should succeed without quota check"""
    db = TestingSessionLocal()
    try:
        # Create test employee
        employee = create_test_employee(db, emp_no=10004, first_name="Alice", last_name="Brown")
        
        # Create unpaid leave request for 20 days (no quota limit)
        payload = {
            "emp_no": 10004,
            "leave_type_id": 1,  # unpaid
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=26)),  # 20 days inclusive
            "employee_comment": "Personal leave"
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["leave_type_id"] == 1
        assert data["status"] == "PENDING"
        assert data["days_requested"] == 20
    finally:
        db.close()


# Test Case 5: Manager approves leave request (quota should be deducted)
def test_manager_approves_leave_request_quota_deducted(client):
    """Test manager approving a leave request - quota should be deducted"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager
        employee = create_test_employee(db, emp_no=10005, first_name="Charlie", last_name="Davis")
        manager = create_test_employee(db, emp_no=20001, first_name="Manager", last_name="One")
        
        # Create leave request for 3 days paid leave
        payload = {
            "emp_no": 10005,
            "leave_type_id": 0,  # paid
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),  # 3 days
            "employee_comment": "Vacation"
        }
        leave_request = client.post("/leave-requests", json=payload).json()
        leave_id = leave_request["leave_id"]
        
        # Check initial quota (should be 10 days default)
        quota_before = db.query(models.EmployeeLeaveQuota).filter(
            models.EmployeeLeaveQuota.emp_no == 10005,
            models.EmployeeLeaveQuota.leave_type_id == 0
        ).first()
        assert quota_before is not None
        initial_quota = quota_before.annual_quota_days
        
        # Manager approves the request
        review_payload = {
            "status": "APPROVED",
            "manager_comment": "Approved for vacation"
        }
        response = client.patch(
            f"/leave-requests/{leave_id}/review?manager_emp_no=20001",
            json=review_payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["manager_emp_no"] == 20001
        assert data["manager_comment"] == "Approved for vacation"
        assert data["decided_at"] is not None
        
        # Verify quota was deducted
        db.refresh(quota_before)
        assert quota_before.annual_quota_days == initial_quota - 3
    finally:
        db.close()


# Test Case 6: Manager rejects leave request (quota should NOT be deducted)
def test_manager_rejects_leave_request_quota_not_deducted(client):
    """Test manager rejecting a leave request - quota should remain unchanged"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager
        employee = create_test_employee(db, emp_no=10006, first_name="Diana", last_name="Miller")
        manager = create_test_employee(db, emp_no=20002, first_name="Manager", last_name="Two")
        
        # Create leave request
        payload = {
            "emp_no": 10006,
            "leave_type_id": 0,  # paid
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),  # 3 days
            "employee_comment": "Vacation"
        }
        leave_request = client.post("/leave-requests", json=payload).json()
        leave_id = leave_request["leave_id"]
        
        # Check initial quota
        quota_before = db.query(models.EmployeeLeaveQuota).filter(
            models.EmployeeLeaveQuota.emp_no == 10006,
            models.EmployeeLeaveQuota.leave_type_id == 0
        ).first()
        initial_quota = quota_before.annual_quota_days
        
        # Manager rejects the request
        review_payload = {
            "status": "REJECTED",
            "manager_comment": "Not approved due to workload"
        }
        response = client.patch(
            f"/leave-requests/{leave_id}/review?manager_emp_no=20002",
            json=review_payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "REJECTED"
        
        # Verify quota was NOT deducted
        db.refresh(quota_before)
        assert quota_before.annual_quota_days == initial_quota
    finally:
        db.close()


# Test Case 7: Try to review non-pending request (should fail)
def test_review_non_pending_request_fails(client):
    """Test that reviewing an already reviewed request should fail"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager
        employee = create_test_employee(db, emp_no=10007, first_name="Eve", last_name="Johnson")
        manager = create_test_employee(db, emp_no=20003, first_name="Manager", last_name="Three")
        
        # Create and approve a request
        payload = {
            "emp_no": 10007,
            "leave_type_id": 1,  # unpaid (no quota issues)
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
        }
        leave_request = client.post("/leave-requests", json=payload).json()
        leave_id = leave_request["leave_id"]
        
        # Approve it first
        review_payload = {"status": "APPROVED"}
        client.patch(
            f"/leave-requests/{leave_id}/review?manager_emp_no=20003",
            json=review_payload
        )
        
        # Try to review again - should fail
        response = client.patch(
            f"/leave-requests/{leave_id}/review?manager_emp_no=20003",
            json={"status": "REJECTED"}
        )
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()
    finally:
        db.close()


# Test Case 8: Multiple requests and quota tracking
def test_multiple_requests_quota_tracking(client):
    """Test creating multiple requests and tracking quota correctly"""
    db = TestingSessionLocal()
    try:
        # Create employee
        employee = create_test_employee(db, emp_no=10008, first_name="Frank", last_name="Williams")
        manager = create_test_employee(db, emp_no=20004, first_name="Manager", last_name="Four")
        
        # Create first request (3 days paid)
        payload1 = {
            "emp_no": 10008,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),  # 3 days
        }
        req1 = client.post("/leave-requests", json=payload1).json()
        
        # Approve first request
        client.patch(
            f"/leave-requests/{req1['leave_id']}/review?manager_emp_no=20004",
            json={"status": "APPROVED"}
        )
        
        # Check quota after first approval (should be 10 - 3 = 7)
        quota = db.query(models.EmployeeLeaveQuota).filter(
            models.EmployeeLeaveQuota.emp_no == 10008,
            models.EmployeeLeaveQuota.leave_type_id == 0
        ).first()
        assert quota.annual_quota_days == 7
        
        # Create second request (4 days paid)
        payload2 = {
            "emp_no": 10008,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=20)),
            "end_date": str(date.today() + timedelta(days=23)),  # 4 days
        }
        req2 = client.post("/leave-requests", json=payload2).json()
        
        # Approve second request
        client.patch(
            f"/leave-requests/{req2['leave_id']}/review?manager_emp_no=20004",
            json={"status": "APPROVED"}
        )
        
        # Check quota after second approval (should be 7 - 4 = 3)
        db.refresh(quota)
        assert quota.annual_quota_days == 3
    finally:
        db.close()


# Test Case 9: List leave requests filtered by status
def test_list_leave_requests_by_status(client):
    """Test listing leave requests filtered by status"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager
        employee = create_test_employee(db, emp_no=10009, first_name="Grace", last_name="Jones")
        manager = create_test_employee(db, emp_no=20005, first_name="Manager", last_name="Five")
        
        # Create multiple requests
        for i in range(3):
            payload = {
                "emp_no": 10009,
                "leave_type_id": 1,  # unpaid
                "start_date": str(date.today() + timedelta(days=7 + i)),
                "end_date": str(date.today() + timedelta(days=8 + i)),
            }
            req = client.post("/leave-requests", json=payload).json()
            
            # Approve first, reject second, leave third pending
            if i == 0:
                client.patch(
                    f"/leave-requests/{req['leave_id']}/review?manager_emp_no=20005",
                    json={"status": "APPROVED"}
                )
            elif i == 1:
                client.patch(
                    f"/leave-requests/{req['leave_id']}/review?manager_emp_no=20005",
                    json={"status": "REJECTED"}
                )
        
        # List all pending requests
        response = client.get("/leave-requests?status=PENDING")
        assert response.status_code == 200
        pending_requests = response.json()
        assert len(pending_requests) >= 1
        assert all(req["status"] == "PENDING" for req in pending_requests)
        
        # List all approved requests
        response = client.get("/leave-requests?status=APPROVED")
        assert response.status_code == 200
        approved_requests = response.json()
        assert len(approved_requests) >= 1
        assert all(req["status"] == "APPROVED" for req in approved_requests)
    finally:
        db.close()


# Test Case 10: List leave requests filtered by employee
def test_list_leave_requests_by_employee(client):
    """Test listing leave requests filtered by employee number"""
    db = TestingSessionLocal()
    try:
        # Create two employees
        emp1 = create_test_employee(db, emp_no=10010, first_name="Henry", last_name="Taylor")
        emp2 = create_test_employee(db, emp_no=10011, first_name="Iris", last_name="Anderson")
        
        # Create requests for both employees
        payload1 = {
            "emp_no": 10010,
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=8)),
        }
        client.post("/leave-requests", json=payload1)
        
        payload2 = {
            "emp_no": 10011,
            "leave_type_id": 1,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=8)),
        }
        client.post("/leave-requests", json=payload2)
        
        # List requests for employee 10010 only
        response = client.get("/leave-requests?emp_no=10010")
        assert response.status_code == 200
        requests = response.json()
        assert len(requests) >= 1
        assert all(req["emp_no"] == 10010 for req in requests)
    finally:
        db.close()

