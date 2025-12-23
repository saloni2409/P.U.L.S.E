import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Authentication endpoints: expect validation errors when payload missing

def test_auth_register_requires_payload():
    resp = client.post("/api/auth/register", json={})
    assert resp.status_code == 422


def test_auth_login_requires_payload():
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 422


# Protected endpoints should return 401 when Authorization header missing

# Foods

def test_foods_search_requires_auth():
    resp = client.get("/api/foods/search", params={"q": "ap"})
    assert resp.status_code == 401


def test_get_food_requires_auth():
    resp = client.get("/api/foods/123")
    assert resp.status_code == 401


def test_get_foods_by_category_requires_auth():
    resp = client.get("/api/foods/category/fruits")
    assert resp.status_code == 401

import pytest

# All tests use the `client` fixture provided by `conftest.py` which configures
# an in-memory SQLite DB and overrides the app's `get_db` dependency.


# Authentication endpoints: expect validation errors when payload missing
def test_auth_register_requires_payload(client):
    resp = client.post("/api/auth/register", json={})
    assert resp.status_code == 422


def test_auth_login_requires_payload(client):
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 422


# Protected endpoints should return 401 when Authorization header missing

# Foods
def test_foods_search_requires_auth(client):
    resp = client.get("/api/foods/search", params={"q": "ap"})
    assert resp.status_code == 401


def test_get_food_requires_auth(client):
    resp = client.get("/api/foods/123")
    assert resp.status_code == 401


def test_get_foods_by_category_requires_auth(client):
    resp = client.get("/api/foods/category/fruits")
    assert resp.status_code == 401


def test_post_food_requires_auth(client):
    resp = client.post("/api/foods", json={"name": "Test Food"})
    assert resp.status_code == 401


def test_get_all_foods_requires_auth(client):
    resp = client.get("/api/foods")
    assert resp.status_code == 401


# Meals-AI
def test_meals_ai_log_ai_requires_auth(client):
    payload = {
        "meal_description": "2 eggs and toast",
        "meal_type": "BREAKFAST",
        "meal_date": "2025-12-23"
    }
    resp = client.post("/api/meals-ai/log-ai", json=payload)
    assert resp.status_code == 401


def test_meals_ai_log_manual_requires_auth(client):
    payload = {
        "meal_description": "Salad",
        "meal_type": "LUNCH",
        "meal_date": "2025-12-23",
        "meal_items": []
    }
    resp = client.post("/api/meals-ai/log-manual", json=payload)
    assert resp.status_code == 401


# Meals
def test_meals_log_requires_auth(client):
    payload = {"meal_description": "Toast", "meal_type": "SNACK", "meal_date": "2025-12-23"}
    resp = client.post("/api/meals/log", json=payload)
    assert resp.status_code == 401


def test_meals_get_all_requires_auth(client):
    resp = client.get("/api/meals/all")
    assert resp.status_code == 401


def test_meals_get_by_date_requires_auth(client):
    resp = client.get("/api/meals/date/2025-12-23")
    assert resp.status_code == 401


def test_get_meal_requires_auth(client):
    resp = client.get("/api/meals/123")
    assert resp.status_code == 401


def test_update_meal_requires_auth(client):
    resp = client.put("/api/meals/123", json={"meal_description": "Updated"})
    assert resp.status_code == 401


def test_delete_meal_requires_auth(client):
    resp = client.delete("/api/meals/123")
    assert resp.status_code == 401


# Meal items
def test_get_meal_items_requires_auth(client):
    resp = client.get("/api/meals/123/items")
    assert resp.status_code == 401


def test_add_meal_item_requires_auth(client):
    resp = client.post("/api/meals/123/items", json={"food_name": "Apple", "quantity": 1})
    assert resp.status_code == 401


def test_update_meal_item_requires_auth(client):
    resp = client.put("/api/meals/123/items/456", json={"quantity": 2})
    assert resp.status_code == 401


def test_delete_meal_item_requires_auth(client):
    resp = client.delete("/api/meals/123/items/456")
    assert resp.status_code == 401


# Nutrition
def test_get_daily_nutrition_requires_auth(client):
    resp = client.get("/api/nutrition/daily/2025-12-23")
    assert resp.status_code == 401


def test_get_weekly_nutrition_requires_auth(client):
    resp = client.get("/api/nutrition/weekly")
    assert resp.status_code == 401


def test_get_range_nutrition_requires_auth(client):
    resp = client.get("/api/nutrition/range", params={"start_date": "2025-12-01", "end_date": "2025-12-07"})
    assert resp.status_code == 401
