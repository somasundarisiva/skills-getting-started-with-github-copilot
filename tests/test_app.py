"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    original = {
        name: {**data, "participants": list(data["participants"])}
        for name, data in activities.items()
    }
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_signup_for_activity():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]


def test_signup_duplicate_raises_error():
    client.post("/activities/Chess Club/signup", params={"email": "dup@mergington.edu"})
    response = client.post("/activities/Chess Club/signup", params={"email": "dup@mergington.edu"})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_from_activity():
    # First sign up
    client.post("/activities/Chess Club/signup", params={"email": "temp@mergington.edu"})
    # Then unregister
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "temp@mergington.edu"},
    )
    assert response.status_code == 200
    assert "temp@mergington.edu" in response.json()["message"]


def test_unregister_not_signed_up():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "ghost@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent/signup",
        params={"email": "student@mergington.edu"},
    )
    assert response.status_code == 404
