import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_data(client):
    # Arrange (implicit)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    activities_data = client.get("/activities").json()
    assert email in activities_data[activity]["participants"]


def test_signup_duplicate_fails(client):
    # Arrange
    activity = "Chess Club"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    activities_data = client.get("/activities").json()
    assert email not in activities_data[activity]["participants"]


def test_unregister_missing_participant_400(client):
    # Arrange
    activity = "Chess Club"
    email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400


def test_unregister_unknown_activity_404(client):
    # Arrange
    activity = "NoSuchClub"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
