"""
Tests for the API events endpoints
Following TDD principles from https://pytest-with-eric.com/tdd/pytest-tdd/
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime

from src.main import app
from src.api.events.models import EventModel, EventCreateSchema


def test_read_events_empty(test_client, test_db):
    """
    Test the events endpoint returns empty results when no events exist
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Using fixtures

    # Act
    response = test_client.get("/api/events/")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_create_event(test_client, test_db):
    """
    Test creating a new event
    
    TDD Step 1: Write a failing test (Red)
    """
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
    response = test_client.post("/api/events/", json=event_data)
    
    # Assert
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["page"] == event_data["page"]
    assert response_data["user_agent"] == event_data["user_agent"]
    assert response_data["ip_address"] == event_data["ip_address"]
    assert response_data["referrer"] == event_data["referrer"]
    assert response_data["session_id"] == event_data["session_id"]
    assert response_data["duration"] == event_data["duration"]
    assert "id" in response_data
    assert "time" in response_data


def test_get_event_by_id(test_client, test_db):
    """
    Test retrieving an event by ID
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # First create an event
    event_data = {
        "page": "/test-page",
        "user_agent": "test-agent",
        "ip_address": "127.0.0.1",
        "referrer": "test-referrer",
        "session_id": "test-session",
        "duration": 30
    }
    create_response = test_client.post("/api/events/", json=event_data)
    event_id = create_response.json()["id"]
    
    # Act
    response = test_client.get(f"/api/events/{event_id}")
    
    # Assert
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["id"] == event_id
    assert response_data["page"] == event_data["page"]
    assert response_data["user_agent"] == event_data["user_agent"]
    assert response_data["ip_address"] == event_data["ip_address"]
    assert response_data["referrer"] == event_data["referrer"]
    assert response_data["session_id"] == event_data["session_id"]
    assert response_data["duration"] == event_data["duration"]


def test_get_nonexistent_event(test_client, test_db):
    """
    Test getting a non-existent event returns 404
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    nonexistent_id = 9999  # Assuming this ID doesn't exist
    
    # Act
    response = test_client.get(f"/api/events/{nonexistent_id}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_read_events_after_creation(test_client, test_db):
    """
    Test that created events appear in the event list
    
    TDD Step 1: Write a failing test (Red)
    """
    # Arrange
    # Create a few events with pages that match the DEFAULT_LOOKUP_PAGES
    event_data_1 = {
        "page": "/",
        "user_agent": "Windows test-agent",
        "duration": 30
    }
    event_data_2 = {
        "page": "/about",
        "user_agent": "MacOS test-agent",
        "duration": 60
    }
    
    # Act
    test_client.post("/api/events/", json=event_data_1)
    test_client.post("/api/events/", json=event_data_2)
    
    response = test_client.get("/api/events/")
    
    # Assert
    assert response.status_code == 200
    results = response.json()
    
    # There should be events returned
    assert len(results) > 0
    
    # Check if our pages are in the results
    pages_in_results = [item["page"] for item in results]
    assert "/" in pages_in_results
    assert "/about" in pages_in_results 