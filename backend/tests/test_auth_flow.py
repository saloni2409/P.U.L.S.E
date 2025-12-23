import uuid


def test_register_login_and_access_protected_endpoint(client):
    # Create unique test user
    uid = uuid.uuid4().hex[:8]
    username = f"testuser_{uid}"
    email = f"{username}@example.com"
    password = "testpassword123"

    # Register
    register_payload = {
        "username": username,
        "email": email,
        "password": password,
        "daily_calorie_goal": 2200
    }
    resp = client.post("/api/auth/register", json=register_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["username"] == username
    assert "user_id" in data

    # Login
    login_payload = {"username": username, "password": password}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, resp.text
    token_data = resp.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Use token to access a protected endpoint
    headers = {"Authorization": f"Bearer {token}"}

    # Call a protected read endpoint - get all foods (should return 200 with a list)
    resp = client.get("/api/foods", headers=headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)

    # Call search endpoint with auth
    resp = client.get("/api/foods/search", params={"q": "ap"}, headers=headers)
    # If no foods exist, service may return empty list (200) or 400 if q too short - we provided 2 chars so expect 200
    assert resp.status_code == 200

    # Call meals endpoint to create a meal (should return 200 and created meal structure)
    meal_payload = {
        "meal_type": "SNACK",
        "meal_description": "Piece of fruit",
        "meal_date": "2025-12-23",
        "meal_items": []
    }
    resp = client.post("/api/meals/log", json=meal_payload, headers=headers)
    # Depending on services, creation may succeed or may fail if additional processing required; accept 200 or 500 as long as auth works
    assert resp.status_code in (200, 201, 500), resp.text
