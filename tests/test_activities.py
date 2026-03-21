"""
API endpoint tests for the FastAPI Mergington High School activities application.
Tests are structured using the Arrange-Act-Assert (AAA) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """
        Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: Create test client (from fixture)
        - Act: Make GET request to /activities
        - Assert: Verify 200 response and activities are in response body
        """
        # Arrange
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Robotics Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        for activity_name in expected_activity_names:
            assert activity_name in response.json()

    def test_get_activities_contains_activity_details(self, client: TestClient, sample_activity_name: str):
        """
        Test that each activity in the response contains required fields.
        
        AAA Pattern:
        - Arrange: Prepare expected fields to verify
        - Act: Make GET request and extract an activity
        - Assert: Verify activity has all required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities.get(sample_activity_name)

        # Assert
        assert activity is not None
        for field in required_fields:
            assert field in activity


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_succeeds(self, client: TestClient, sample_activity_name: str, sample_email: str):
        """
        Test successful signup of a new student to an activity.
        
        AAA Pattern:
        - Arrange: Get initial participant count
        - Act: Send POST request to signup endpoint
        - Assert: Verify 200 response and participant was added
        """
        # Arrange
        get_response = client.get("/activities")
        initial_participant_count = len(get_response.json()[sample_activity_name]["participants"])

        # Act
        signup_response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert signup_response.status_code == 200
        assert sample_email in signup_response.json()["message"]
        
        # Verify participant was actually added
        verify_response = client.get("/activities")
        final_participant_count = len(verify_response.json()[sample_activity_name]["participants"])
        assert final_participant_count == initial_participant_count + 1
        assert sample_email in verify_response.json()[sample_activity_name]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client: TestClient, nonexistent_activity_name: str, sample_email: str):
        """
        Test that signup to a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare non-existent activity name and email
        - Act: Send POST request with invalid activity name
        - Assert: Verify 404 response with appropriate error message
        """
        # Arrange
        # (fixtures already provide what we need)

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity_name}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_student_returns_400(self, client: TestClient, sample_activity_name: str, existing_participant_email: str):
        """
        Test that signuping up an already-enrolled student returns 400.
        
        AAA Pattern:
        - Arrange: Use an email already enrolled in the activity
        - Act: Send POST request with duplicate email
        - Assert: Verify 400 response with appropriate error message
        """
        # Arrange
        # (existing_participant_email is already enrolled in sample_activity_name)

        # Act
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": existing_participant_email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_existing_participant_succeeds(self, client: TestClient, sample_activity_name: str, existing_participant_email: str):
        """
        Test successful removal of an existing participant from an activity.
        
        AAA Pattern:
        - Arrange: Verify participant is enrolled
        - Act: Send DELETE request to remove participant
        - Assert: Verify 200 response and participant is removed
        """
        # Arrange
        get_response = client.get("/activities")
        assert existing_participant_email in get_response.json()[sample_activity_name]["participants"]

        # Act
        delete_response = client.delete(
            f"/activities/{sample_activity_name}/participants/{existing_participant_email}"
        )

        # Assert
        assert delete_response.status_code == 200
        assert existing_participant_email in delete_response.json()["message"]
        
        # Verify participant was actually removed
        verify_response = client.get("/activities")
        assert existing_participant_email not in verify_response.json()[sample_activity_name]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client: TestClient, nonexistent_activity_name: str, sample_email: str):
        """
        Test that removing a participant from a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Prepare non-existent activity name and email
        - Act: Send DELETE request with invalid activity name
        - Assert: Verify 404 response with appropriate error message
        """
        # Arrange
        # (fixtures already provide what we need)

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity_name}/participants/{sample_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_non_participant_returns_404(self, client: TestClient, sample_activity_name: str, sample_email: str):
        """
        Test that removing a non-enrolled student returns 404.
        
        AAA Pattern:
        - Arrange: Ensure the email is not enrolled in the activity
        - Act: Send DELETE request for non-enrolled participant
        - Assert: Verify 404 response with appropriate error message
        """
        # Arrange
        get_response = client.get("/activities")
        assert sample_email not in get_response.json()[sample_activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{sample_activity_name}/participants/{sample_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"].lower()
