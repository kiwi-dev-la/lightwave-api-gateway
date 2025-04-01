"""
Tests for the API health endpoint
Following TDD principles from https://pytest-with-eric.com/tdd/pytest-tdd/
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_health_endpoint(test_client):
    """
    Test the health endpoint returns status "ok"
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Using the test_client fixture

    # Act
    response = test_client.get("/healthz")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_endpoint_wrong_method(test_client):
    """
    Test that the health endpoint rejects POST requests
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Using the test_client fixture

    # Act
    response = test_client.post("/healthz")
    
    # Assert
    assert response.status_code == 405  # Method Not Allowed 