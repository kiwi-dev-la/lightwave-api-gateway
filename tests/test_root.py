"""
Tests for the API root endpoint
Following TDD principles from https://pytest-with-eric.com/tdd/pytest-tdd/
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_root_endpoint(test_client):
    """
    Test the root endpoint returns the hello world message
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Using the test_client fixture

    # Act
    response = test_client.get("/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_root_endpoint_wrong_method(test_client):
    """
    Test that the root endpoint rejects POST requests
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Using the test_client fixture

    # Act
    response = test_client.post("/")
    
    # Assert
    assert response.status_code == 405  # Method Not Allowed 