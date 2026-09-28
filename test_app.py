from base64 import b64encode


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text
    assert "Generate 7-Day Plan" in response.text


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["ai_mode"] == "demo"


def test_generate_and_lookup(client):
    payload = {
        "username": "Alex",
        "user_id": "alex-001",
        "age": 28,
        "weight": 72,
        "goal": "muscle gain",
        "intensity": "medium",
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["plan_id"] > 0
    assert "Day 1" in data["workout_plan"]
    assert data["nutrition_tip"]

    lookup = client.get("/api/users/alex-001")
    assert lookup.status_code == 200
    assert lookup.json()["user"]["username"] == "Alex"
    assert lookup.json()["plan"]["original_plan"]


def test_feedback_update(client):
    payload = {
        "username": "Sam",
        "user_id": "sam-001",
        "age": 31,
        "weight": 68,
        "goal": "general wellness",
        "intensity": "low",
    }
    assert client.post("/api/generate", json=payload).status_code == 200

    response = client.post(
        "/api/feedback",
        json={"user_id": "sam-001", "feedback": "Add more cardio."},
    )
    assert response.status_code == 200
    assert "Add more cardio." in response.json()["updated_plan"]


def test_admin_api_requires_auth(client):
    assert client.get("/api/users").status_code == 401

    token = b64encode(b"admin:test-password").decode()
    response = client.get("/api/users", headers={"Authorization": f"Basic {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
