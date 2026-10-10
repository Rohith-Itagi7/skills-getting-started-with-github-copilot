from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_get_activities_returns_data():
    response = client.get("/activities")
    expected_new_activities = {
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club",
    }

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]
    assert expected_new_activities <= response.json().keys()


def test_signup_for_activity_success():
    activity_name = "Chess Club"
    original_participants = list(activities[activity_name]["participants"])
    email = "new-student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]

    activities[activity_name]["participants"] = original_participants


def test_signup_for_activity_rejects_duplicate_email():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_for_activity_rejects_unknown_activity():
    response = client.post("/activities/Unknown Activity/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_rejects_full_activity():
    activity_name = "Gym Class"
    original_participants = list(activities[activity_name]["participants"])
    activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(activities[activity_name]["max_participants"])
    ]

    try:
        response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")

        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
    finally:
        activities[activity_name]["participants"] = original_participants
