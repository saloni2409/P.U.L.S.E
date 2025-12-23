import uuid


def test_meal_crud_flow(client):
    # Create unique test user
    uid = uuid.uuid4().hex[:8]
    username = f"mealuser_{uid}"
    email = f"{username}@example.com"
    password = "strongpass123"

    # Register
    register_payload = {
        "username": username,
        "email": email,
        "password": password,
    }
    resp = client.post("/api/auth/register", json=register_payload)
    assert resp.status_code == 200, resp.text

    # Login
    login_payload = {"username": username, "password": password}
    resp = client.post("/api/auth/login", json=login_payload)
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a meal
    meal_payload = {
        "meal_type": "LUNCH",
        "meal_description": "Test lunch for CRUD",
        "meal_date": "2025-12-23",
        "meal_items": [{"food_name": "Apple", "quantity": 1, "unit": "PIECES"}]
    }
    resp = client.post("/api/meals/log", json=meal_payload, headers=headers)
    assert resp.status_code in (200, 201), resp.text
    meal = resp.json()
    assert "meal_id" in meal
    meal_id = meal["meal_id"]

    # Retrieve the meal
    resp = client.get(f"/api/meals/{meal_id}", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["meal_description"] == "Test lunch for CRUD"

    # Update the meal
    update_payload = {"meal_description": "Updated lunch description"}
    resp = client.put(f"/api/meals/{meal_id}", json=update_payload, headers=headers)
    assert resp.status_code == 200, resp.text
    updated = resp.json()
    assert updated["meal_description"] == "Updated lunch description"

    # Delete the meal
    resp = client.delete(f"/api/meals/{meal_id}", headers=headers)
    assert resp.status_code == 204, resp.text

    # Confirm deletion
    resp = client.get(f"/api/meals/{meal_id}", headers=headers)
    assert resp.status_code == 404
