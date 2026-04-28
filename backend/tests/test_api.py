import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "StepOne AI - Content & Design Engine API"
    assert data["status"] == "running"


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_session(client):
    """Test session creation"""
    response = client.post(
        "/api/v1/sessions",
        json={
            "event_name": "Test Event",
            "event_date": "2024-01-15",
            "location": "Test Location",
            "client_name": "Test Client"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["event_name"] == "Test Event"
    assert "_id" in data


def test_get_sessions(client):
    """Test getting all sessions"""
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_get_session(client):
    """Test getting a specific session"""
    # First create a session
    create_response = client.post(
        "/api/v1/sessions",
        json={
            "event_name": "Test Event 2",
            "event_date": "2024-01-16",
            "location": "Test Location 2",
            "client_name": "Test Client 2"
        }
    )
    session_id = create_response.json()["_id"]
    
    # Get the session
    response = client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == session_id
    assert data["event_name"] == "Test Event 2"


def test_update_session(client):
    """Test updating a session"""
    # Create a session
    create_response = client.post(
        "/api/v1/sessions",
        json={
            "event_name": "Test Event 3",
            "event_date": "2024-01-17",
            "location": "Test Location 3",
            "client_name": "Test Client 3"
        }
    )
    session_id = create_response.json()["_id"]
    
    # Update the session
    response = client.put(
        f"/api/v1/sessions/{session_id}",
        json={"status": "completed"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_delete_session(client):
    """Test deleting a session"""
    # Create a session
    create_response = client.post(
        "/api/v1/sessions",
        json={
            "event_name": "Test Event 4",
            "event_date": "2024-01-18",
            "location": "Test Location 4",
            "client_name": "Test Client 4"
        }
    )
    session_id = create_response.json()["_id"]
    
    # Delete the session
    response = client.delete(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    
    # Verify deletion
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404
