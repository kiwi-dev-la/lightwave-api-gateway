"""
Simple tests for the API
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.fixture
def app():
    """Create a test application with a mocked database"""
    # Create a new FastAPI app for testing
    app = FastAPI()
    
    # Add the routes we want to test
    @app.get("/")
    def read_root():
        return {"Hello": "World"}
    
    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str = None):
        return {"item_id": item_id, "q": q}
    
    @app.get("/healthz")
    def read_api_health():
        return {"status": "ok"}
    
    return app


@pytest.fixture
def client(app):
    """Test client using the test app"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_items_endpoint(client):
    """Test the items endpoint with a valid ID"""
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": None}


def test_items_endpoint_with_query(client):
    """Test the items endpoint with a query parameter"""
    response = client.get("/items/42?q=test")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42, "q": "test"}


# This is how we can run tests against the actual app
# Create two patches - one for init_db and one for get_session
@pytest.fixture
def real_app_client():
    """Test client using the real app with mocked database functions"""
    from src.main import app
    
    # First patch: completely disable the init_db function from being called
    with patch('src.api.db.session.init_db') as mock_init_db:
        mock_init_db.return_value = None
        
        # Second patch: mock the database session for all routes
        with patch('src.api.db.session.get_session') as mock_get_session:
            mock_session = Mock()
            mock_session.exec.return_value.fetchall.return_value = []
            mock_get_session.return_value = mock_session
            
            # Create the test client with our patches
            with TestClient(app) as client:
                yield client


def test_real_app_health(real_app_client):
    """Test the health endpoint on the real app"""
    response = real_app_client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 