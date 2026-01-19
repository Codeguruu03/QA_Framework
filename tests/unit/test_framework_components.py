"""
Unit Tests for Framework Components

These tests verify the framework components work correctly
WITHOUT needing a real backend server. They test:
- Configuration loading
- Authentication manager
- API client initialization
- Page object instantiation
"""

import pytest
from unittest.mock import MagicMock, patch
import os


class TestConfigUnit:
    """Unit tests for the Config module."""
    
    def test_get_environment_default(self):
        """Test: Default environment is staging."""
        from utils.config import Config, Environment
        
        # When no env var set, should default to staging
        with patch.dict(os.environ, {}, clear=True):
            env = Config.get_environment()
            assert env == Environment.STAGING
    
    def test_get_environment_from_env_var(self):
        """Test: Environment can be set via env var."""
        from utils.config import Config, Environment
        
        with patch.dict(os.environ, {"TEST_ENV": "production"}):
            env = Config.get_environment()
            assert env == Environment.PRODUCTION
    
    def test_get_browser_default(self):
        """Test: Default browser is chromium."""
        from utils.config import Config, Browser
        
        with patch.dict(os.environ, {}, clear=True):
            browser = Config.get_browser()
            assert browser == Browser.CHROMIUM
    
    def test_is_headless_default(self):
        """Test: Default is headless mode."""
        from utils.config import Config
        
        with patch.dict(os.environ, {}, clear=True):
            assert Config.is_headless() == True
    
    def test_get_tenant_exists(self):
        """Test: Can retrieve existing tenant config."""
        from utils.config import Config
        
        tenant = Config.get_tenant("company1")
        assert tenant.tenant_id == "company1"
        assert tenant.admin_email == "admin@company1.com"
    
    def test_get_tenant_not_exists(self):
        """Test: Raises error for unknown tenant."""
        from utils.config import Config
        
        with pytest.raises(ValueError, match="Unknown tenant"):
            Config.get_tenant("unknown_company")
    
    def test_get_api_base_url(self):
        """Test: API base URL is returned correctly."""
        from utils.config import Config
        
        url = Config.get_api_base_url()
        assert url.startswith("http")
        assert "/api/v1" in url
    
    def test_browser_launch_options(self):
        """Test: Browser launch options are valid."""
        from utils.config import Config
        
        options = Config.get_browser_launch_options()
        assert "headless" in options
        assert isinstance(options["headless"], bool)


class TestAuthManagerUnit:
    """Unit tests for the AuthManager module."""
    
    def test_auth_token_is_expired(self):
        """Test: Token expiry detection works."""
        from utils.auth import AuthToken
        import time
        
        # Expired token
        expired_token = AuthToken(
            access_token="test",
            expires_at=time.time() - 100  # Expired 100 seconds ago
        )
        assert expired_token.is_expired() == True
        
        # Valid token
        valid_token = AuthToken(
            access_token="test",
            expires_at=time.time() + 3600  # Expires in 1 hour
        )
        assert valid_token.is_expired() == False
    
    def test_auth_token_is_valid(self):
        """Test: Token validity check works."""
        from utils.auth import AuthToken
        import time
        
        valid_token = AuthToken(
            access_token="test_token",
            expires_at=time.time() + 3600
        )
        assert valid_token.is_valid() == True
        
        empty_token = AuthToken(
            access_token="",
            expires_at=time.time() + 3600
        )
        assert empty_token.is_valid() == False
    
    def test_auth_manager_cache_clear(self):
        """Test: Auth manager can clear cache."""
        from utils.auth import AuthManager
        
        auth = AuthManager()
        auth._token_cache[("test", "test@test.com")] = MagicMock()
        
        auth.clear_cache()
        
        assert len(auth._token_cache) == 0
    
    def test_get_test_credentials(self):
        """Test: Can get test credentials for tenant."""
        from utils.auth import get_test_credentials
        
        email, password = get_test_credentials("company1", "admin")
        assert email == "admin@company1.com"
        assert password is not None


class TestAPIClientUnit:
    """Unit tests for the APIClient module."""
    
    def test_api_client_initialization(self):
        """Test: API client initializes correctly."""
        from utils.api_client import APIClient
        
        client = APIClient(
            base_url="https://api.example.com",
            token="test_token",
            tenant_id="company1"
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.tenant_id == "company1"
        assert "Bearer test_token" in client.headers["Authorization"]
        assert client.headers["X-Tenant-ID"] == "company1"
    
    def test_api_client_set_token(self):
        """Test: Can update auth token."""
        from utils.api_client import APIClient
        
        client = APIClient(
            base_url="https://api.example.com",
            token="old_token",
            tenant_id="company1"
        )
        
        client.set_token("new_token")
        
        assert "Bearer new_token" in client.headers["Authorization"]
    
    def test_api_client_set_tenant(self):
        """Test: Can update tenant ID."""
        from utils.api_client import APIClient
        
        client = APIClient(
            base_url="https://api.example.com",
            token="token",
            tenant_id="company1"
        )
        
        client.set_tenant("company2")
        
        assert client.tenant_id == "company2"
        assert client.headers["X-Tenant-ID"] == "company2"


class TestPageObjectsUnit:
    """Unit tests for Page Object classes."""
    
    def test_login_page_initialization(self):
        """Test: LoginPage initializes correctly."""
        from pages.login_page import LoginPage
        
        mock_page = MagicMock()
        login = LoginPage(mock_page)
        
        assert login.page == mock_page
        assert login.base_url == "https://app.workflowpro.com"
    
    def test_login_page_custom_base_url(self):
        """Test: LoginPage accepts custom base URL."""
        from pages.login_page import LoginPage
        
        mock_page = MagicMock()
        login = LoginPage(mock_page, base_url="https://custom.example.com")
        
        assert login.base_url == "https://custom.example.com"
    
    def test_dashboard_page_initialization(self):
        """Test: DashboardPage initializes correctly."""
        from pages.dashboard_page import DashboardPage
        
        mock_page = MagicMock()
        dashboard = DashboardPage(mock_page)
        
        assert dashboard.page == mock_page
    
    def test_base_page_has_required_methods(self):
        """Test: BasePage has all required methods."""
        from pages.base_page import BasePage
        
        mock_page = MagicMock()
        base = BasePage(mock_page)
        
        # Verify required methods exist
        assert hasattr(base, 'navigate_to')
        assert hasattr(base, 'click')
        assert hasattr(base, 'fill')
        assert hasattr(base, 'get_text')
        assert hasattr(base, 'is_visible')
        assert hasattr(base, 'wait_for_element')


class TestFrameworkIntegrity:
    """Tests to verify framework components work together."""
    
    def test_all_modules_import(self):
        """Test: All framework modules can be imported."""
        # These should not raise any exceptions
        from utils.config import Config, Environment, Browser, TenantConfig
        from utils.auth import AuthManager, AuthToken, auth_manager
        from utils.api_client import APIClient
        from pages.base_page import BasePage
        from pages.login_page import LoginPage
        from pages.dashboard_page import DashboardPage
        
        assert True  # If we get here, all imports succeeded
    
    def test_tenant_configs_consistent(self):
        """Test: All tenant configs have required fields."""
        from utils.config import Config
        
        for tenant_id in ["company1", "company2", "company3"]:
            tenant = Config.get_tenant(tenant_id)
            
            assert tenant.tenant_id == tenant_id
            assert tenant.admin_email is not None
            assert tenant.admin_password is not None
            assert tenant.base_url is not None
    
    def test_user_roles_defined(self):
        """Test: User roles are properly defined."""
        from utils.config import Config
        
        assert "admin" in Config.USER_ROLES
        assert "manager" in Config.USER_ROLES
        assert "employee" in Config.USER_ROLES
        
        # Admin should have all permissions
        admin_perms = Config.USER_ROLES["admin"]
        assert admin_perms["can_create_project"] == True
        assert admin_perms["can_delete_project"] == True
        assert admin_perms["can_manage_users"] == True
