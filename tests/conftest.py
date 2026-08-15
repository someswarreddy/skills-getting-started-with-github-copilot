"""Pytest configuration and fixtures for the Mergington High School Activities API tests."""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for making requests."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities dictionary before each test.
    This ensures test isolation by providing a clean copy of initial data.
    """
    # Store the original state
    original_activities = copy.deepcopy(activities)
    
    # Yield control to the test
    yield
    
    # Reset to original state after the test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_test_data():
    """Provide sample test data for email addresses and activity names."""
    return {
        "emails": [
            "test.student@mergington.edu",
            "new.student@mergington.edu",
            "another.student@mergington.edu",
        ],
        "activities": [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Club",
            "Science Olympiad",
            "Art Club",
            "Music Ensemble",
        ],
        "invalid_activity": "Nonexistent Activity",
    }
