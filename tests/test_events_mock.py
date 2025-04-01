"""
Tests for the events API with complete DB mocking
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.api.db.session import get_session


@pytest.fixture
def mock_time_bucket():
    """Mock the time_bucket function from timescaledb"""
    with patch('src.api.events.routing.time_bucket') as mock:
        # Configure the mock to work in the query
        mock.return_value.label.return_value = "bucket_column"
        yield mock


@pytest.fixture
def mock_events_response():
    """Mock event data for testing"""
    return [
        {
            "bucket": "2023-06-01T00:00:00",
            "operating_system": "Windows",
            "page": "/",
            "avg_duration": 45.5,
            "count": 10
        },
        {
            "bucket": "2023-06-01T00:00:00",
            "operating_system": "MacOS",
            "page": "/about",
            "avg_duration": 30.2,
            "count": 5
        }
    ]


@pytest.fixture
def mock_session(mock_events_response):
    """Create a completely mocked database session"""
    session = MagicMock()
    
    # Mock exec().fetchall() to return event data
    exec_mock = MagicMock()
    exec_mock.fetchall.return_value = mock_events_response
    session.exec.return_value = exec_mock
    
    # Mock add() method for event creation
    session.add = MagicMock()
    
    # Mock commit() method
    session.commit = MagicMock()
    
    # Mock refresh() to simulate adding ID to created object
    def refresh_side_effect(obj):
        obj.id = 1
        obj.time = "2023-06-01T12:00:00"
    
    session.refresh.side_effect = refresh_side_effect
    
    return session


@pytest.fixture
def client(mock_session, mock_time_bucket):
    """Create a FastAPI TestClient with mocked dependencies"""
    
    # Mock the get_session dependency
    def override_get_session():
        yield mock_session
    
    # Override the get_session dependency
    app.dependency_overrides[get_session] = override_get_session
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides = {}


def test_read_events(client, mock_events_response):
    """Test getting events list"""
    response = client.get("/api/events/")
    
    assert response.status_code == 200
    assert response.json() == mock_events_response


def test_create_event(client):
    """Test creating a new event"""
    event_data = {
        "page": "/test-page",
        "user_agent": "test-agent",
        "ip_address": "127.0.0.1",
        "referrer": "test-referrer",
        "session_id": "test-session",
        "duration": 30
    }
    
    response = client.post("/api/events/", json=event_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["page"] == event_data["page"] 