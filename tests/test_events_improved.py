"""
Improved tests for the events API with complete mocking
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.api.events.models import EventModel


@pytest.fixture
def mock_event():
    """Create a mock event for testing"""
    event = MagicMock(spec=EventModel)
    event.id = 1
    event.page = "/test-page"
    event.user_agent = "test-agent"
    event.ip_address = "127.0.0.1"
    event.referrer = "test-referrer"
    event.session_id = "test-session"
    event.duration = 30
    event.time = "2023-06-01T12:00:00"
    return event


@pytest.fixture
def mock_db(mock_event):
    """Create a mocked database session"""
    session = MagicMock()
    
    # Configure default behavior for exec().fetchall()
    mock_results = []
    session.exec.return_value.fetchall.return_value = mock_results
    
    # Configure behavior for exec().first() to return event when queried
    def mock_first_side_effect():
        return mock_event
        
    session.exec.return_value.first.side_effect = mock_first_side_effect
    
    # Mock session.add to do nothing
    session.add = MagicMock()
    
    # Mock commit to do nothing
    session.commit = MagicMock()
    
    # Mock refresh to set ID and time on the object
    def mock_refresh_side_effect(obj):
        obj.id = 1
        obj.time = "2023-06-01T12:00:00"
    
    session.refresh.side_effect = mock_refresh_side_effect
    
    return session


@pytest.fixture
def client(mock_db):
    """Create a test client with mocked database session"""
    # Mock time_bucket from timescaledb
    with patch('src.api.events.routing.time_bucket') as mock_time_bucket:
        # Configure the mock to work in the query
        mock_time_bucket.return_value.label.return_value = "bucket_column"
        
        # Mock the database initialization
        with patch('src.api.db.session.init_db') as mock_init_db:
            # Mock the get_session dependency
            with patch('src.api.db.session.get_session') as mock_get_session:
                # Configure get_session to yield our mock session
                def get_session_override():
                    yield mock_db
                    
                mock_get_session.return_value = get_session_override()
                
                # Create the test client
                with TestClient(app) as test_client:
                    yield test_client


def test_get_event(client, mock_event):
    """Test getting an event by ID"""
    # Arrange in fixtures
    
    # Act
    response = client.get(f"/api/events/{mock_event.id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == mock_event.id
    assert data["page"] == mock_event.page


def test_create_event(client):
    """Test creating a new event"""
    # Arrange
    event_data = {
        "page": "/test-page",
        "user_agent": "test-agent",
        "ip_address": "127.0.0.1",
        "referrer": "test-referrer",
        "session_id": "test-session",
        "duration": 30
    }
    
    # Act
    response = client.post("/api/events/", json=event_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["page"] == event_data["page"]
    assert data["time"] == "2023-06-01T12:00:00"


def test_read_events_empty(client, mock_db):
    """Test reading events when none exist"""
    # Arrange - Configure mock to return empty list
    mock_db.exec.return_value.fetchall.return_value = []
    
    # Act
    response = client.get("/api/events/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_read_events(client, mock_db):
    """Test reading events when some exist"""
    # Arrange - Configure mock to return event data
    mock_results = [
        {
            "bucket": "2023-06-01T00:00:00",
            "operating_system": "Windows",
            "page": "/",
            "avg_duration": 45.5,
            "count": 10
        }
    ]
    mock_db.exec.return_value.fetchall.return_value = mock_results
    
    # Act
    response = client.get("/api/events/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == mock_results 