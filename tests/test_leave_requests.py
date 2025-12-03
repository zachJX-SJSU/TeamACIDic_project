from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

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


def setup_department_tables(db: Session):
    """Helper to create dept_emp and dept_manager tables for testing"""
    # Create dept_emp table if not exists (SQLite compatible)
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS dept_emp (
            emp_no INTEGER NOT NULL,
            dept_no VARCHAR(4) NOT NULL,
            from_date DATE NOT NULL,
            to_date DATE NOT NULL,
            PRIMARY KEY (emp_no, dept_no)
        )
    """))
    
    # Create dept_manager table if not exists (SQLite compatible)
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS dept_manager (
            emp_no INTEGER NOT NULL,
            dept_no VARCHAR(4) NOT NULL,
            from_date DATE NOT NULL,
            to_date DATE NOT NULL,
            PRIMARY KEY (emp_no, dept_no)
        )
    """))
    db.commit()


def create_department_assignment(db: Session, emp_no: int, dept_no: str, from_date: str = "2020-01-01", to_date: str = "9999-01-01"):
    """Helper to create a department assignment"""
    db.execute(text("""
        INSERT OR REPLACE INTO dept_emp (emp_no, dept_no, from_date, to_date)
        VALUES (:emp_no, :dept_no, :from_date, :to_date)
    """), {
        "emp_no": emp_no,
        "dept_no": dept_no,
        "from_date": from_date,
        "to_date": to_date
    })
    db.commit()


def create_department_manager(db: Session, manager_emp_no: int, dept_no: str, from_date: str = "2020-01-01", to_date: str = "9999-01-01"):
    """Helper to create a department manager assignment"""
    db.execute(text("""
        INSERT OR REPLACE INTO dept_manager (emp_no, dept_no, from_date, to_date)
        VALUES (:emp_no, :dept_no, :from_date, :to_date)
    """), {
        "emp_no": manager_emp_no,
        "dept_no": dept_no,
        "from_date": from_date,
        "to_date": to_date
    })
    db.commit()


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


# Test Case 11: Manager auto-assigned when creating leave request
def test_manager_auto_assigned_on_leave_request_creation(client):
    """Test that manager_emp_no is automatically set when creating a leave request"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager with unique IDs
        employee = create_test_employee(db, emp_no=50010, first_name="Jack", last_name="Black")
        manager = create_test_employee(db, emp_no=60010, first_name="Manager", last_name="Boss")
        
        # Create department assignment (dept_emp) using raw SQL
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_emp (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        # Create department manager assignment (dept_manager) using raw SQL
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_manager (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        # Use a unique department (d010) to avoid conflicts with other tests
        # Clean up any existing assignments for this test employee
        db.execute(text("DELETE FROM dept_emp WHERE emp_no = :emp_no"), {"emp_no": 50010})
        db.execute(text("""
            INSERT INTO dept_emp (emp_no, dept_no, from_date, to_date)
            VALUES (:emp_no, 'd010', '2020-01-01', '9999-01-01')
        """), {"emp_no": 50010})
        
        # Clean up any existing managers for d010 and create our test manager
        db.execute(text("DELETE FROM dept_manager WHERE dept_no = 'd010'"))
        db.execute(text("""
            INSERT INTO dept_manager (emp_no, dept_no, from_date, to_date)
            VALUES (60010, 'd010', '2020-01-01', '9999-01-01')
        """))
        db.commit()
        
        # Create leave request
        payload = {
            "emp_no": 50010,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
            "employee_comment": "Vacation"
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["manager_emp_no"] == 60010, f"Expected manager_emp_no=60010, got {data.get('manager_emp_no')}"
        assert data["status"] == "PENDING"
    finally:
        db.close()


# Test Case 12: Manager auto-assigned with multiple departments (uses latest)
def test_manager_auto_assigned_latest_department(client):
    """Test that manager from latest department is used when employee has multiple departments"""
    db = TestingSessionLocal()
    try:
        # Create employee and two managers
        employee = create_test_employee(db, emp_no=20011, first_name="Jill", last_name="White")
        manager1 = create_test_employee(db, emp_no=30011, first_name="Manager", last_name="One")
        manager2 = create_test_employee(db, emp_no=30012, first_name="Manager", last_name="Two")
        
        # Create department assignments - employee moved from d001 to d002
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_emp (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        # Old department (ended)
        db.execute(text("""
            INSERT OR REPLACE INTO dept_emp (emp_no, dept_no, from_date, to_date)
            VALUES (:emp_no, 'd001', '2020-01-01', '2023-12-31')
        """), {"emp_no": 20011})
        # Current department (latest)
        db.execute(text("""
            INSERT OR REPLACE INTO dept_emp (emp_no, dept_no, from_date, to_date)
            VALUES (:emp_no, 'd002', '2024-01-01', '9999-01-01')
        """), {"emp_no": 20011})
        
        # Create department managers
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_manager (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        db.execute(text("""
            INSERT OR REPLACE INTO dept_manager (emp_no, dept_no, from_date, to_date)
            VALUES (30011, 'd001', '2020-01-01', '9999-01-01')
        """))
        db.execute(text("""
            INSERT OR REPLACE INTO dept_manager (emp_no, dept_no, from_date, to_date)
            VALUES (30012, 'd002', '2024-01-01', '9999-01-01')
        """))
        db.commit()
        
        # Create leave request - should use manager from d002 (latest department)
        payload = {
            "emp_no": 20011,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert data["manager_emp_no"] == 30012, f"Expected manager from latest dept (30012), got {data.get('manager_emp_no')}"
    finally:
        db.close()


# Test Case 13: No manager assigned when employee has no department
def test_no_manager_when_no_department(client):
    """Test that manager_emp_no is None when employee has no current department"""
    db = TestingSessionLocal()
    try:
        # Create employee without department assignment
        employee = create_test_employee(db, emp_no=20012, first_name="John", last_name="Doe")
        
        # Create leave request
        payload = {
            "emp_no": 20012,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        # manager_emp_no should be None since employee has no department
        assert data["manager_emp_no"] is None, f"Expected manager_emp_no=None, got {data.get('manager_emp_no')}"
    finally:
        db.close()


# Test Case 14: No manager assigned when department has no manager
def test_no_manager_when_department_has_no_manager(client):
    """Test that manager_emp_no is None when department has no current manager"""
    db = TestingSessionLocal()
    try:
        # Create employee
        employee = create_test_employee(db, emp_no=20013, first_name="Jane", last_name="Smith")
        
        # Create department assignment but no manager
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_emp (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        db.execute(text("""
            INSERT OR REPLACE INTO dept_emp (emp_no, dept_no, from_date, to_date)
            VALUES (:emp_no, 'd003', '2020-01-01', '9999-01-01')
        """), {"emp_no": 20013})
        # Don't create any manager for d003
        db.commit()
        
        # Create leave request
        payload = {
            "emp_no": 20013,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        # manager_emp_no should be None since department has no manager
        assert data["manager_emp_no"] is None
    finally:
        db.close()


# Test Case 15: Manager auto-assigned and then manager approves request
def test_manager_auto_assigned_then_manager_approves(client):
    """Test complete workflow: manager auto-assigned, then same manager approves"""
    db = TestingSessionLocal()
    try:
        # Create employee and manager
        employee = create_test_employee(db, emp_no=20014, first_name="Bob", last_name="Johnson")
        manager = create_test_employee(db, emp_no=30014, first_name="Manager", last_name="Boss")
        
        # Set up department and manager
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_emp (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS dept_manager (
                emp_no INTEGER NOT NULL,
                dept_no VARCHAR(4) NOT NULL,
                from_date DATE NOT NULL,
                to_date DATE NOT NULL,
                PRIMARY KEY (emp_no, dept_no)
            )
        """))
        db.execute(text("""
            INSERT OR REPLACE INTO dept_emp (emp_no, dept_no, from_date, to_date)
            VALUES (:emp_no, 'd004', '2020-01-01', '9999-01-01')
        """), {"emp_no": 20014})
        db.execute(text("""
            INSERT OR REPLACE INTO dept_manager (emp_no, dept_no, from_date, to_date)
            VALUES (30014, 'd004', '2020-01-01', '9999-01-01')
        """))
        db.commit()
        
        # Create leave request - manager should be auto-assigned
        payload = {
            "emp_no": 20014,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=7)),
            "end_date": str(date.today() + timedelta(days=9)),
        }
        leave_request = client.post("/leave-requests", json=payload).json()
        leave_id = leave_request["leave_id"]
        
        # Verify manager was auto-assigned
        assert leave_request["manager_emp_no"] == 30014
        
        # Manager approves the request
        review_payload = {
            "status": "APPROVED",
            "manager_comment": "Approved by auto-assigned manager"
        }
        response = client.patch(
            f"/leave-requests/{leave_id}/review?manager_emp_no=30014",
            json=review_payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "APPROVED"
        assert data["manager_emp_no"] == 30014
    finally:
        db.close()


# Test Case 16: Invalid employee when creating leave request
def test_invalid_employee_returns_404(client):
    """Test that creating leave request for non-existent employee returns 404"""
    payload = {
        "emp_no": 99999,  # Non-existent employee
        "leave_type_id": 0,
        "start_date": str(date.today() + timedelta(days=7)),
        "end_date": str(date.today() + timedelta(days=9)),
    }
    
    response = client.post("/leave-requests", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# Test Case 17: Invalid dates when creating leave request
def test_invalid_dates_returns_400(client):
    """Test that creating leave request with end_date < start_date returns 400"""
    db = TestingSessionLocal()
    try:
        employee = create_test_employee(db, emp_no=20015, first_name="Alice", last_name="Brown")
        
        payload = {
            "emp_no": 20015,
            "leave_type_id": 0,
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=5)),  # End before start
        }
        
        response = client.post("/leave-requests", json=payload)
        assert response.status_code == 400
        assert "end_date" in response.json()["detail"].lower() or "date" in response.json()["detail"].lower()
    finally:
        db.close()

