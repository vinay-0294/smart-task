"""
API tests for Smart Task Tracker.
Includes happy path and error path tests as required.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import database as db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    db.reset_db()
    yield


# --- Happy Path Tests ---

class TestProjectsHappyPath:
    """Happy path tests for projects API."""
    
    def test_create_project_success(self):
        """Test creating a project successfully."""
        response = client.post("/api/projects", json={"name": "My Test Project"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Test Project"
        assert "id" in data
    
    def test_list_projects_success(self):
        """Test listing projects."""
        # Create some projects first
        client.post("/api/projects", json={"name": "Project A"})
        client.post("/api/projects", json={"name": "Project B"})
        
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Project A"
        assert data[1]["name"] == "Project B"


class TestTasksHappyPath:
    """Happy path tests for tasks API."""
    
    def test_create_task_success(self):
        """Test creating a task successfully."""
        # Create project first
        project_resp = client.post("/api/projects", json={"name": "Test Project"})
        project_id = project_resp.json()["id"]
        
        # Create task
        response = client.post(
            f"/api/projects/{project_id}/tasks",
            json={
                "title": "My First Task",
                "description": "This is a test task",
                "status": "Todo",
                "priority": "High"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My First Task"
        assert data["priority"] == "High"
        assert data["status"] == "Todo"
        assert data["project_id"] == project_id
    
    def test_list_tasks_with_status_filter(self):
        """Test listing tasks with status filter."""
        # Create project and tasks
        project_resp = client.post("/api/projects", json={"name": "Filter Test"})
        project_id = project_resp.json()["id"]
        
        # Create tasks with different statuses
        client.post(f"/api/projects/{project_id}/tasks", 
                   json={"title": "Task 1", "status": "Todo", "priority": "Med"})
        client.post(f"/api/projects/{project_id}/tasks", 
                   json={"title": "Task 2", "status": "In-Progress", "priority": "High"})
        client.post(f"/api/projects/{project_id}/tasks", 
                   json={"title": "Task 3", "status": "Done", "priority": "Low"})
        
        # Filter by status
        response = client.get(f"/api/projects/{project_id}/tasks?status=Todo")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 1"
        
        # Get all tasks
        response = client.get(f"/api/projects/{project_id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_update_task_success(self):
        """Test updating a task successfully."""
        # Create project and task
        project_resp = client.post("/api/projects", json={"name": "Update Test"})
        project_id = project_resp.json()["id"]
        task_resp = client.post(
            f"/api/projects/{project_id}/tasks",
            json={"title": "Original Title", "status": "Todo", "priority": "Low"}
        )
        task_id = task_resp.json()["id"]
        
        # Update task
        response = client.patch(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title", "status": "In-Progress", "priority": "High"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "In-Progress"
        assert data["priority"] == "High"


class TestAIIntakeHappyPath:
    """Happy path tests for AI intake API."""
    
    def test_ai_intake_extracts_title_and_priority(self):
        """Test AI intake extracts title and detects priority."""
        response = client.post(
            "/api/ai/intake",
            json={"input": "I need to urgently fix the login bug on the homepage. Users are complaining."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "priority" in data
        assert data["priority"] == "High"  # "urgently" keyword
    
    def test_ai_intake_low_priority(self):
        """Test AI intake detects low priority."""
        response = client.post(
            "/api/ai/intake",
            json={"input": "When possible, add a dark mode toggle to settings. Nice to have feature."}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "Low"  # "when possible", "nice to have"


# --- Error Path Tests ---

class TestProjectsErrorPath:
    """Error path tests for projects API."""
    
    def test_create_duplicate_project_fails(self):
        """Test creating a project with duplicate name fails."""
        # Create first project
        client.post("/api/projects", json={"name": "Duplicate Name"})
        
        # Try to create duplicate
        response = client.post("/api/projects", json={"name": "Duplicate Name"})
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_create_project_empty_name_fails(self):
        """Test creating a project with empty name fails."""
        response = client.post("/api/projects", json={"name": ""})
        assert response.status_code == 422  # Validation error


class TestTasksErrorPath:
    """Error path tests for tasks API."""
    
    def test_create_task_nonexistent_project_fails(self):
        """Test creating a task for non-existent project fails."""
        response = client.post(
            "/api/projects/99999/tasks",
            json={"title": "Orphan Task", "status": "Todo", "priority": "Med"}
        )
        assert response.status_code == 404
        assert "project not found" in response.json()["detail"].lower()
    
    def test_update_nonexistent_task_fails(self):
        """Test updating a non-existent task fails."""
        response = client.patch(
            "/api/tasks/99999",
            json={"title": "Ghost Task"}
        )
        assert response.status_code == 404
        assert "task not found" in response.json()["detail"].lower()
    
    def test_list_tasks_nonexistent_project_fails(self):
        """Test listing tasks for non-existent project fails."""
        response = client.get("/api/projects/99999/tasks")
        assert response.status_code == 404
        assert "project not found" in response.json()["detail"].lower()


class TestAIIntakeErrorPath:
    """Error path tests for AI intake API."""
    
    def test_ai_intake_empty_input_fails(self):
        """Test AI intake with empty input fails validation."""
        response = client.post("/api/ai/intake", json={"input": ""})
        assert response.status_code == 422  # Validation error

