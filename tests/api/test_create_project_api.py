"""
API Tests for Project CRUD Operations

Tests for the WorkFlow Pro API endpoints including:
- Project creation, retrieval, update, delete
- Error handling and validation
- Tenant isolation at API level
"""

import pytest
import uuid

from utils.api_client import APIClient
from utils.auth import auth_manager
from utils.config import Config


class TestCreateProjectAPI:
    """Tests for the POST /api/v1/projects endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client for tests."""
        self.client = APIClient(
            base_url=Config.get_api_base_url(),
            token=auth_manager.get_tenant_auth("company1")["Authorization"].replace("Bearer ", ""),
            tenant_id="company1"
        )
        self.created_ids = []
        yield
        # Cleanup
        for project_id in self.created_ids:
            try:
                self.client.delete_project(project_id)
            except Exception:
                pass
    
    def test_create_project_success(self):
        """Test: Successfully create a project via API."""
        payload = {
            "name": f"API Test Project {uuid.uuid4().hex[:8]}",
            "description": "Created via API",
            "team_members": ["user1@test.com", "user2@test.com"]
        }
        
        response = self.client.create_project(payload)
        self.created_ids.append(response.get("id"))
        
        assert response["name"] == payload["name"]
        assert response["status"] == "active"
        assert "id" in response
    
    def test_create_project_minimal_data(self):
        """Test: Create project with minimal required data."""
        payload = {
            "name": f"Minimal Project {uuid.uuid4().hex[:8]}",
            "description": "",
            "team_members": []
        }
        
        response = self.client.create_project(payload)
        self.created_ids.append(response.get("id"))
        
        assert response["name"] == payload["name"]
        assert response["status"] == "active"
    
    def test_create_project_with_special_characters(self):
        """Test: Create project with special characters in name."""
        payload = {
            "name": f"Project (Test) #1 - {uuid.uuid4().hex[:8]}",
            "description": "Special chars: @#$%^&*()",
            "team_members": []
        }
        
        response = self.client.create_project(payload)
        self.created_ids.append(response.get("id"))
        
        assert response["name"] == payload["name"]


class TestProjectCRUD:
    """Tests for full CRUD operations on projects."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client and create a test project."""
        self.client = APIClient(
            base_url=Config.get_api_base_url(),
            token=auth_manager.get_tenant_auth("company1")["Authorization"].replace("Bearer ", ""),
            tenant_id="company1"
        )
        
        # Create a test project
        self.project = self.client.create_project({
            "name": f"CRUD Test Project {uuid.uuid4().hex[:8]}",
            "description": "For CRUD testing",
            "team_members": []
        })
        self.project_id = self.project.get("id")
        
        yield
        
        # Cleanup
        try:
            self.client.delete_project(self.project_id)
        except Exception:
            pass
    
    def test_get_project(self):
        """Test: Retrieve a project by ID."""
        response = self.client.get_project(self.project_id)
        
        assert response["id"] == self.project_id
        assert response["name"] == self.project["name"]
    
    def test_update_project(self):
        """Test: Update a project's details."""
        new_name = f"Updated Project {uuid.uuid4().hex[:8]}"
        response = self.client.update_project(self.project_id, {
            "name": new_name,
            "description": "Updated description"
        })
        
        assert response["name"] == new_name
    
    def test_list_projects(self):
        """Test: List all projects for tenant."""
        response = self.client.list_projects()
        
        # Should return a list structure
        assert "projects" in response or isinstance(response, list)
    
    def test_delete_project(self):
        """Test: Delete a project."""
        # Create a project specifically for deletion
        project = self.client.create_project({
            "name": f"Delete Test {uuid.uuid4().hex[:8]}",
            "description": "",
            "team_members": []
        })
        
        # Delete it
        self.client.delete_project(project["id"])
        
        # Verify it's deleted (should raise 404)
        with pytest.raises(Exception):
            self.client.get_project(project["id"])


class TestAPIErrorHandling:
    """Tests for API error handling and edge cases."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client."""
        self.client = APIClient(
            base_url=Config.get_api_base_url(),
            token=auth_manager.get_tenant_auth("company1")["Authorization"].replace("Bearer ", ""),
            tenant_id="company1"
        )
    
    def test_get_nonexistent_project(self):
        """Test: Attempting to get non-existent project returns error."""
        with pytest.raises(Exception):
            self.client.get_project(99999999)
    
    def test_invalid_token_rejected(self):
        """Test: Invalid auth token is rejected."""
        invalid_client = APIClient(
            base_url=Config.get_api_base_url(),
            token="invalid_token_12345",
            tenant_id="company1"
        )
        
        with pytest.raises(Exception):
            invalid_client.list_projects()


class TestAPITenantIsolation:
    """Tests specifically for API-level tenant isolation."""
    
    @pytest.mark.tenant_isolation
    def test_cannot_access_other_tenant_project(self):
        """Test: Cannot access projects from another tenant."""
        # Create project as Company1
        company1_client = APIClient(
            base_url=Config.get_api_base_url(),
            token=auth_manager.get_tenant_auth("company1")["Authorization"].replace("Bearer ", ""),
            tenant_id="company1"
        )
        
        project = company1_client.create_project({
            "name": f"Isolation Test {uuid.uuid4().hex[:8]}",
            "description": "Security test",
            "team_members": []
        })
        project_id = project["id"]
        
        try:
            # Try to access as Company2
            company2_client = APIClient(
                base_url=Config.get_api_base_url(),
                token=auth_manager.get_tenant_auth("company2")["Authorization"].replace("Bearer ", ""),
                tenant_id="company2"
            )
            
            # Should not find this project
            with pytest.raises(Exception):
                company2_client.get_project(project_id)
                
        finally:
            company1_client.delete_project(project_id)
