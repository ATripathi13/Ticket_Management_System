def test_create_and_get_ticket(client):
    # register and login
    client.post("/api/v1/auth/register", json={"email": "u1@ex.com", "password": "p", "role": "user"})
    login = client.post("/api/v1/auth/login", data={"username": "u1@ex.com", "password": "p"})
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create Ticket
    response = client.post(
        "/api/v1/tickets/",
        json={"title": "Test Bug", "description": "Fix the bug", "priority": "high", "category": "bug"},
        headers=headers
    )
    assert response.status_code == 200
    ticket_id = response.json()["id"]
    assert response.json()["title"] == "Test Bug"

    # Get Ticket
    get_res = client.get(f"/api/v1/tickets/{ticket_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Test Bug"
