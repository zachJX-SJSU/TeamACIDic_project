from datetime import date


def test_create_employee(client):
    payload = {
        "birth_date": "1990-01-01",
        "first_name": "John",
        "last_name": "Smith",
        "gender": "M",
        "hire_date": "2020-01-01",
    }
    response = client.post("/employees", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "emp_no" in data
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["gender"] == payload["gender"]
    assert data["hire_date"] == payload["hire_date"]


def test_list_employees(client):
    # Should at least return the previously created employee
    response = client.get("/employees")
    assert response.status_code == 200

    employees = response.json()
    assert isinstance(employees, list)
    assert len(employees) >= 1


def test_get_employee_by_id(client):
    # Create an employee first
    payload = {
        "birth_date": "1991-02-02",
        "first_name": "Alice",
        "last_name": "Brown",
        "gender": "F",
        "hire_date": "2021-02-02",
    }
    created = client.post("/employees", json=payload).json()
    emp_no = created["emp_no"]

    response = client.get(f"/employees/{emp_no}")
    assert response.status_code == 200

    data = response.json()
    assert data["emp_no"] == emp_no
    assert data["first_name"] == "Alice"


def test_update_employee(client):
    # Create
    payload = {
        "birth_date": "1992-03-03",
        "first_name": "Bob",
        "last_name": "Taylor",
        "gender": "M",
        "hire_date": "2022-03-03",
    }
    created = client.post("/employees", json=payload).json()
    emp_no = created["emp_no"]

    # Update
    update_payload = {"first_name": "Robert"}
    response = client.put(f"/employees/{emp_no}", json=update_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["emp_no"] == emp_no
    assert data["first_name"] == "Robert"


def test_delete_employee(client):
    payload = {
        "birth_date": "1993-04-04",
        "first_name": "Carol",
        "last_name": "Lee",
        "gender": "F",
        "hire_date": "2023-04-04",
    }
    created = client.post("/employees", json=payload).json()
    emp_no = created["emp_no"]

    # Delete
    response = client.delete(f"/employees/{emp_no}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/employees/{emp_no}")
    assert response.status_code == 404
