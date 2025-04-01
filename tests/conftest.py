"""
Pytest configuration and fixtures for API testing
"""
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from sqlmodel import SQLModel as Base


# Create a mock function for init_db
def mock_init_db():
    """Mock implementation of init_db that does nothing"""
    print("Mock database initialization")
    return None


# Patch the init_db function in the main module
@pytest.fixture(scope="session", autouse=True)
def patch_init_db():
    """
    Patch the init_db function to prevent actual database connection
    """
    with patch('src.api.db.session.init_db', mock_init_db):
        yield


# Create a mock session
@pytest.fixture
def mock_db():
    """
    Create a mock database session
    """
    return MagicMock()


# Add a test_db fixture that's used in the tests
@pytest.fixture
def test_db():
    """
    Create a mock database session for testing
    This fixture is used in test_events.py
    """
    db = MagicMock()
    # Mock the exec method to return an object with fetchall method
    db.exec.return_value.fetchall.return_value = []
    # Mock the add method
    db.add = MagicMock()
    # Mock the commit method
    db.commit = MagicMock()
    # Mock the refresh method
    db.refresh = MagicMock()
    # Mock the exec.first method for single item queries
    db.exec.return_value.first.return_value = None
    return db


# Override get_session to return the mock session
@pytest.fixture
def override_get_session(mock_db):
    """
    Override the get_session dependency
    """
    def _override_get_session():
        yield mock_db
    return _override_get_session


@pytest.fixture
def test_client(override_get_session):
    """
    Create a test client for the FastAPI application with mocked dependencies
    """
    from src.main import app
    from src.api.db.session import get_session
    
    # Override the get_session dependency with our mock
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides = {} 