"""
API Client Module

Provides a REST API client for testing WorkFlow Pro backend services
with proper error handling, retries, and multi-tenant support.
"""

import requests
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:
    """
    REST API client for WorkFlow Pro services.
    
    Features:
    - Multi-tenant support (X-Tenant-ID header)
    - Automatic retries for transient failures
    - Proper error handling
    - CRUD operations for projects
    
    Usage:
        client = APIClient(
            base_url="https://api.workflowpro.com",
            token="your_token",
            tenant_id="company1"
        )
        project = client.create_project({"name": "Test", ...})
    """
    
    def __init__(self, base_url: str, token: str, tenant_id: str):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "X-Tenant-ID": tenant_id,
            "Content-Type": "application/json"
        }
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    # =========================================================================
    # Project CRUD Operations
    # =========================================================================
    
    def create_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            payload: Project data with name, description, team_members
            
        Returns:
            Created project data with id, name, status
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/projects",
            json=payload,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Get a project by ID."""
        response = self.session.get(
            f"{self.base_url}/api/v1/projects/{project_id}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def list_projects(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """List all projects for the tenant."""
        response = self.session.get(
            f"{self.base_url}/api/v1/projects",
            params={"page": page, "limit": limit},
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def update_project(self, project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project."""
        response = self.session.put(
            f"{self.base_url}/api/v1/projects/{project_id}",
            json=payload,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def delete_project(self, project_id: int) -> None:
        """Delete a project."""
        response = self.session.delete(
            f"{self.base_url}/api/v1/projects/{project_id}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
    
    # =========================================================================
    # Team Member Operations
    # =========================================================================
    
    def add_team_member(self, project_id: int, user_email: str) -> Dict[str, Any]:
        """Add a team member to a project."""
        response = self.session.post(
            f"{self.base_url}/api/v1/projects/{project_id}/members",
            json={"email": user_email},
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def remove_team_member(self, project_id: int, user_email: str) -> None:
        """Remove a team member from a project."""
        response = self.session.delete(
            f"{self.base_url}/api/v1/projects/{project_id}/members/{user_email}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    def health_check(self) -> bool:
        """Check if the API is healthy."""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def set_token(self, token: str) -> None:
        """Update the authentication token."""
        self.headers["Authorization"] = f"Bearer {token}"
    
    def set_tenant(self, tenant_id: str) -> None:
        """Update the tenant ID."""
        self.tenant_id = tenant_id
        self.headers["X-Tenant-ID"] = tenant_id
