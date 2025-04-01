"""
Simpler tests that don't rely on database connections
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """
    Test client that bypasses database connections
    """
    # Create a mock for init_db that does nothing
    with patch('src.api.db.session.init_db'):
        # Also mock the get_session function
        with patch('src.api.events.routing.get_session', return_value=MagicMock()):
            with TestClient(app) as test_client:
                yield test_client


def test_health_endpoint(client):
    """
    Test that the health endpoint returns status ok
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """
    Test that the root endpoint returns Hello World
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_items_endpoint(client):
    """
    Test that the items endpoint returns the expected data
    """
    item_id = 42
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": None} 