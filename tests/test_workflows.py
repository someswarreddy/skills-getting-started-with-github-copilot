"""Integration tests for Mergington High School Activities API workflows."""
import pytest


class TestSignupRemovalWorkflows:
    """Test suite for multi-step workflows combining signup and removal."""

    def test_signup_remove_signup_workflow(self, client, reset_activities, sample_test_data):
        """Verify the workflow: signup → remove → signup again."""
        email = sample_test_data["emails"][0]
        activity = sample_test_data["activities"][0]
        
        # Step 1: First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Verify participant is present
        response_check1 = client.get("/activities")
        assert email in response_check1.json()[activity]["participants"]
        
        # Step 2: Remove participant
        response2 = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify participant is gone
        response_check2 = client.get("/activities")
        assert email not in response_check2.json()[activity]["participants"]
        
        # Step 3: Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify participant is back
        response_check3 = client.get("/activities")
        assert email in response_check3.json()[activity]["participants"]

    def test_multiple_students_signup_for_same_activity(self, client, reset_activities, sample_test_data):
        """Verify that multiple students can sign up for the same activity."""
        activity = sample_test_data["activities"][0]
        students = sample_test_data["emails"][:3]
        
        # Sign up all students
        for email in students:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students are signed up
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in students:
            assert email in participants

    def test_remove_one_student_among_many(self, client, reset_activities, sample_test_data):
        """Verify that removing one student doesn't affect others."""
        activity = sample_test_data["activities"][0]
        students = sample_test_data["emails"][:3]
        
        # Sign up all students
        for email in students:
            client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
        
        # Remove the second student
        email_to_remove = students[1]
        response = client.delete(
            f"/activities/{activity}/remove",
            params={"email": email_to_remove}
        )
        assert response.status_code == 200
        
        # Verify only the specified student is removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email_to_remove not in participants
        assert students[0] in participants
        assert students[2] in participants

    def test_student_signup_multiple_activities(self, client, reset_activities, sample_test_data):
        """Verify that a student can sign up for multiple activities."""
        email = sample_test_data["emails"][0]
        activities = sample_test_data["activities"][:3]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]

    def test_student_removed_from_one_activity_stays_in_others(self, client, reset_activities, sample_test_data):
        """Verify that removing from one activity doesn't affect other activities."""
        email = sample_test_data["emails"][0]
        activities = sample_test_data["activities"][:3]
        
        # Sign up for multiple activities
        for activity in activities:
            client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
        
        # Remove from the second activity
        activity_to_remove_from = activities[1]
        response = client.delete(
            f"/activities/{activity_to_remove_from}/remove",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify student is removed from only that activity
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_to_remove_from]["participants"]
        assert email in data[activities[0]]["participants"]
        assert email in data[activities[2]]["participants"]


class TestParticipantCounting:
    """Test suite for verifying participant count accuracy during operations."""

    def test_participant_count_after_signup(self, client, reset_activities, sample_test_data):
        """Verify that participant count is accurate after signup."""
        activity = sample_test_data["activities"][0]
        email = sample_test_data["emails"][0]
        
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Verify count increased
        response_after = client.get("/activities")
        new_count = len(response_after.json()[activity]["participants"])
        assert new_count == initial_count + 1

    def test_participant_count_after_removal(self, client, reset_activities, sample_test_data):
        """Verify that participant count is accurate after removal."""
        activity = sample_test_data["activities"][0]
        email = sample_test_data["emails"][0]
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Get count before removal
        response_before = client.get("/activities")
        count_before_removal = len(response_before.json()[activity]["participants"])
        
        # Remove
        client.delete(f"/activities/{activity}/remove", params={"email": email})
        
        # Verify count decreased
        response_after = client.get("/activities")
        count_after_removal = len(response_after.json()[activity]["participants"])
        assert count_after_removal == count_before_removal - 1
