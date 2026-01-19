"""
Configuration Management Module

Handles multiple environments, browsers, and test data configuration
for the WorkFlow Pro B2B SaaS testing framework.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Environment(Enum):
    """Supported test environments."""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Browser(Enum):
    """Supported browsers for testing."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"  # Safari


class Platform(Enum):
    """Supported platforms for cross-platform testing."""
    WEB = "web"
    IOS = "ios"
    ANDROID = "android"


@dataclass
class TenantConfig:
    """Configuration for a specific tenant/company."""
    tenant_id: str
    subdomain: str
    admin_email: str
    admin_password: str
    
    @property
    def base_url(self) -> str:
        """Generate the base URL for this tenant."""
        env = Config.get_environment()
        if env == Environment.LOCAL:
            return f"http://localhost:3000"
        elif env == Environment.STAGING:
            return f"https://{self.subdomain}.staging.workflowpro.com"
        else:
            return f"https://{self.subdomain}.workflowpro.com"


@dataclass 
class BrowserStackConfig:
    """BrowserStack cloud testing configuration."""
    username: str
    access_key: str
    project_name: str = "WorkFlow Pro Tests"
    build_name: str = "Automated Tests"
    
    @property
    def hub_url(self) -> str:
        return f"https://{self.username}:{self.access_key}@hub-cloud.browserstack.com/wd/hub"


class Config:
    """
    Central configuration management for the test framework.
    
    Usage:
        config = Config()
        api_url = config.api_base_url
        tenant = config.get_tenant("company1")
    """
    
    # Environment variable keys
    ENV_KEY = "TEST_ENV"
    BROWSER_KEY = "TEST_BROWSER"
    HEADLESS_KEY = "HEADLESS"
    BS_USERNAME_KEY = "BROWSERSTACK_USERNAME"
    BS_ACCESS_KEY = "BROWSERSTACK_ACCESS_KEY"
    
    # Default timeouts (in milliseconds)
    DEFAULT_TIMEOUT = 15000
    ELEMENT_TIMEOUT = 10000
    NAVIGATION_TIMEOUT = 30000
    
    # API Configuration
    API_ENDPOINTS = {
        Environment.LOCAL: "http://localhost:8000/api/v1",
        Environment.STAGING: "https://api.staging.workflowpro.com/api/v1",
        Environment.PRODUCTION: "https://api.workflowpro.com/api/v1",
    }
    
    # Tenant configurations
    TENANTS = {
        "company1": TenantConfig(
            tenant_id="company1",
            subdomain="company1",
            admin_email="admin@company1.com",
            admin_password=os.getenv("COMPANY1_PASSWORD", "password123"),
        ),
        "company2": TenantConfig(
            tenant_id="company2",
            subdomain="company2",
            admin_email="admin@company2.com",
            admin_password=os.getenv("COMPANY2_PASSWORD", "password123"),
        ),
        "company3": TenantConfig(
            tenant_id="company3",
            subdomain="company3",
            admin_email="admin@company3.com",
            admin_password=os.getenv("COMPANY3_PASSWORD", "password123"),
        ),
    }
    
    # User roles for permission testing
    USER_ROLES = {
        "admin": {"can_create_project": True, "can_delete_project": True, "can_manage_users": True},
        "manager": {"can_create_project": True, "can_delete_project": False, "can_manage_users": False},
        "employee": {"can_create_project": False, "can_delete_project": False, "can_manage_users": False},
    }
    
    @classmethod
    def get_environment(cls) -> Environment:
        """Get the current test environment."""
        env_str = os.getenv(cls.ENV_KEY, "staging").lower()
        try:
            return Environment(env_str)
        except ValueError:
            return Environment.STAGING
    
    @classmethod
    def get_browser(cls) -> Browser:
        """Get the configured browser for testing."""
        browser_str = os.getenv(cls.BROWSER_KEY, "chromium").lower()
        try:
            return Browser(browser_str)
        except ValueError:
            return Browser.CHROMIUM
    
    @classmethod
    def is_headless(cls) -> bool:
        """Check if tests should run in headless mode."""
        return os.getenv(cls.HEADLESS_KEY, "true").lower() == "true"
    
    @classmethod
    def get_tenant(cls, tenant_id: str) -> TenantConfig:
        """Get configuration for a specific tenant."""
        if tenant_id not in cls.TENANTS:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        return cls.TENANTS[tenant_id]
    
    @classmethod
    def get_api_base_url(cls) -> str:
        """Get the API base URL for the current environment."""
        env = cls.get_environment()
        return cls.API_ENDPOINTS[env]
    
    @classmethod
    def get_browserstack_config(cls) -> Optional[BrowserStackConfig]:
        """Get BrowserStack configuration if available."""
        username = os.getenv(cls.BS_USERNAME_KEY)
        access_key = os.getenv(cls.BS_ACCESS_KEY)
        
        if username and access_key:
            return BrowserStackConfig(
                username=username,
                access_key=access_key,
            )
        return None
    
    @classmethod
    def get_browser_launch_options(cls) -> dict:
        """Get browser launch options for Playwright."""
        return {
            "headless": cls.is_headless(),
            "slow_mo": 0 if cls.is_headless() else 100,  # Slow down for debugging
        }
    
    @classmethod
    def get_context_options(cls) -> dict:
        """Get browser context options for Playwright."""
        return {
            "viewport": {"width": 1280, "height": 720},
            "ignore_https_errors": cls.get_environment() != Environment.PRODUCTION,
        }


# Convenience instances
config = Config()
