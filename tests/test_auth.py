def test_register(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "role": "user"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "password123",
        "role": "user"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
