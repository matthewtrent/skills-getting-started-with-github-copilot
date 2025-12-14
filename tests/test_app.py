"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original_activities = {
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and friendly matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly tournaments",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills through debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu", "lisa@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots to compete in regional competitions",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["maya@mergington.edu", "chris@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["jessica@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Tennis Club" in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_list(self, client, reset_activities):
        """Test that participants list is correct"""
        response = client.get("/activities")
        data = response.json()
        assert data["Basketball Team"]["participants"] == ["alex@mergington.edu"]
        assert len(data["Debate Team"]["participants"]) == 2


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup fails"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup properly adds participant"""
        initial_count = len(activities["Tennis Club"]["participants"])
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert len(activities["Tennis Club"]["participants"]) == initial_count + 1


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "alex@mergington.edu" not in activities["Basketball Team"]["participants"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister for student not signed up"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister properly removes participant"""
        initial_count = len(activities["Debate Team"]["participants"])
        response = client.post(
            "/activities/Debate%20Team/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        assert len(activities["Debate Team"]["participants"]) == initial_count - 1


class TestIntegration:
    """Integration tests for signup and unregister workflow"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Chess%20Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
    
    def test_cannot_unregister_after_unregister(self, client, reset_activities):
        """Test that unregistering twice fails"""
        email = "alex@mergington.edu"
        activity = "Basketball%20Team"
        
        # First unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Second unregister should fail
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
