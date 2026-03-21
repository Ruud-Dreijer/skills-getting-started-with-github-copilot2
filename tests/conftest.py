"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add src directory to path for importing the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


# Store the original activities state for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture
def client():
    """
    Fixture providing a TestClient instance for the FastAPI application.
    Resets the activities database to original state before each test for isolation.
    
    Yields:
        TestClient: A test client for making HTTP requests to the app
    """
    # Reset activities to original state before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    
    yield TestClient(app)
    
    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def sample_email():
    """
    Fixture providing a sample email for testing.
    
    Returns:
        str: A sample student email address
    """
    return "test.student@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """
    Fixture providing a sample activity name for testing.
    
    Returns:
        str: An activity name that exists in the in-memory database
    """
    return "Chess Club"


@pytest.fixture
def nonexistent_activity_name():
    """
    Fixture providing an activity name that doesn't exist.
    
    Returns:
        str: A non-existent activity name
    """
    return "Nonexistent Activity"


@pytest.fixture
def existing_participant_email():
    """
    Fixture providing an email of a participant already enrolled in Chess Club.
    
    Returns:
        str: An email of an existing Chess Club participant
    """
    return "michael@mergington.edu"
