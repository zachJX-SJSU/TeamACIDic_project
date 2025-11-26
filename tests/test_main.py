def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert body["message"] == "HR Portal backend is running"
