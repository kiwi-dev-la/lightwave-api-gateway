"""
Basic tests for the events endpoints focusing just on the API
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from src.main import app


@pytest.fixture
def mock_db():
    """Create a simple mock database session"""
    db = MagicMock()
    # Mock the exec method for queries
    db.exec = MagicMock()
    db.exec.return_value.fetchall = MagicMock(return_value=[])
    db.exec.return_value.first = MagicMock(return_value=None)
    
    # Mock methods for creating records
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    
    return db


@pytest.fixture
def client(mock_db):
    """Create a test client with all necessary database functions mocked"""
    # First patch init_db to prevent database connection on startup
    with patch('src.api.db.session.init_db') as mock_init_db:
        mock_init_db.return_value = None  # Do nothing
        
        # Then patch get_session to return our mock
        with patch('src.api.db.session.get_session') as mock_get_session:
            def override_get_session():
                yield mock_db
            mock_get_session.return_value = override_get_session()
            
            # Also patch time_bucket which is used in queries
            with patch('src.api.events.routing.time_bucket') as mock_time_bucket:
                mock_time_bucket.return_value.label.return_value = "mocked_bucket"
                
                # Create test client
                with TestClient(app) as test_client:
                    yield test_client


def test_health_endpoint(client):
    """Test the health endpoint works"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_events_empty(client, mock_db):
    """Test getting events when none exist"""
    # Configure mock to return empty results
    mock_db.exec.return_value.fetchall.return_value = []
    
    # Make request
    response = client.get("/api/events/")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == []


def test_get_events_with_data(client, mock_db):
    """Test getting events when some exist"""
    # Configure mock to return some event data
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
    
    # Make request
    response = client.get("/api/events/")
    
    # Verify response
    assert response.status_code == 200
    assert response.json() == mock_results


def test_get_event_not_found(client, mock_db):
    """Test getting a non-existent event"""
    # Configure mock to return None (no event found)
    mock_db.exec.return_value.first.return_value = None
    
    # Make request
    response = client.get("/api/events/999")
    
    # Verify response
    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"} 