"""
Tests for the API items endpoint
Following TDD principles from https://pytest-with-eric.com/tdd/pytest-tdd/
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


def test_items_endpoint_valid_id(test_client):
    """
    Test the items endpoint with a valid ID
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    item_id = 42
    
    # Act
    response = test_client.get(f"/items/{item_id}")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": None}


def test_items_endpoint_with_query(test_client):
    """
    Test the items endpoint with a query parameter
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    item_id = 42
    query = "test-query"
    
    # Act
    response = test_client.get(f"/items/{item_id}?q={query}")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id, "q": query}


def test_items_endpoint_invalid_id(test_client):
    """
    Test the items endpoint with an invalid ID (non-integer)
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    invalid_id = "abc"  # String instead of integer
    
    # Act
    response = test_client.get(f"/items/{invalid_id}")
    
    # Assert
    assert response.status_code == 422  # Unprocessable Entity 