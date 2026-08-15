"""Parametrized tests for Mergington High School Activities API endpoints."""
import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Verify that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected activities are present
        expected_activities = {
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Debate Club",
            "Science Olympiad",
            "Art Club",
            "Music Ensemble",
        }
        assert set(data.keys()) == expected_activities

    def test_get_activities_response_structure(self, client, reset_activities):
        """Verify that each activity has the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            
            # Verify types
            assert isinstance(details["description"], str)
            assert isinstance(details["schedule"], str)
            assert isinstance(details["max_participants"], int)
            assert isinstance(details["participants"], list)

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
    ])
    def test_get_activities_specific_activity(self, client, reset_activities, activity_name):
        """Verify that specific activities are included in the response."""
        response = client.get("/activities")
        data = response.json()
        assert activity_name in data


class TestRootRedirect:
    """Test suite for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Verify that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, client, reset_activities, sample_test_data):
        """Verify that a new student can successfully sign up for an activity."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_successful_signup_adds_participant(self, client, reset_activities, sample_test_data):
        """Verify that the participant is actually added to the activity."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        # Signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Verify participant is in the list
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants

    def test_duplicate_signup_returns_400(self, client, reset_activities, sample_test_data):
        """Verify that attempting to sign up twice returns a 400 error."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Attempt duplicate signup
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities, sample_test_data):
        """Verify that signing up for a nonexistent activity returns 404."""
        email = sample_test_data["emails"][0]
        invalid_activity = sample_test_data["invalid_activity"]
        
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.parametrize("email", [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu",
    ])
    def test_multiple_students_signup(self, client, reset_activities, email):
        """Verify that multiple students can sign up for the same activity."""
        activity = "Programming Class"
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200


class TestRemoveFromActivity:
    """Test suite for DELETE /activities/{activity_name}/remove endpoint."""

    def test_successful_removal(self, client, reset_activities, sample_test_data):
        """Verify that a participant can be successfully removed."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        # First, signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Then, remove
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()

    def test_removal_actually_removes_participant(self, client, reset_activities, sample_test_data):
        """Verify that the participant is actually removed from the activity."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        # Signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Remove
        client.delete(f"/activities/{activity}/remove", params={"email": email})
        
        # Verify participant is no longer in the list
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_remove_nonexistent_participant_returns_400(self, client, reset_activities, sample_test_data):
        """Verify that removing a non-signed-up student returns 400."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_remove_from_nonexistent_activity_returns_404(self, client, reset_activities, sample_test_data):
        """Verify that removing from a nonexistent activity returns 404."""
        email = sample_test_data["emails"][0]
        invalid_activity = sample_test_data["invalid_activity"]
        
        response = client.delete(
            f"/activities/{invalid_activity}/remove",
            params={"email": email}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.parametrize("activity", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
    ])
    def test_remove_from_different_activities(self, client, reset_activities, activity):
        """Verify removal works across different activities."""
        email = "test.student@mergington.edu"
        
        # Signup
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Remove
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response.status_code == 200
