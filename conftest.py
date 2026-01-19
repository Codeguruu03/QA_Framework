"""
Pytest Configuration and Shared Fixtures

This conftest.py provides shared fixtures for:
- Browser/page management (Playwright)
- API client instances
- Authentication
- Test data cleanup
- BrowserStack integration
"""

import pytest
from typing import Generator, Optional
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext

from utils.config import Config, Browser as BrowserType, TenantConfig
from utils.auth import AuthManager, auth_manager
from utils.api_client import APIClient


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def config() -> Config:
    """Provide access to the configuration singleton."""
    return Config()


@pytest.fixture(scope="session")
def auth() -> AuthManager:
    """Provide access to the authentication manager."""
    return auth_manager


# ============================================================================
# Browser Fixtures (Playwright)
# ============================================================================

@pytest.fixture(scope="session")
def playwright_instance():
    """Create a Playwright instance for the test session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Generator[Browser, None, None]:
    """
    Create a browser instance for the test session.
    
    The browser type is determined by the TEST_BROWSER environment variable.
    """
    browser_type = Config.get_browser()
    launch_options = Config.get_browser_launch_options()
    
    if browser_type == BrowserType.CHROMIUM:
        browser = playwright_instance.chromium.launch(**launch_options)
    elif browser_type == BrowserType.FIREFOX:
        browser = playwright_instance.firefox.launch(**launch_options)
    elif browser_type == BrowserType.WEBKIT:
        browser = playwright_instance.webkit.launch(**launch_options)
    else:
        browser = playwright_instance.chromium.launch(**launch_options)
    
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context_options = Config.get_context_options()
    context = browser.new_context(**context_options)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)
    yield page
    page.close()


# ============================================================================
# Tenant-specific Fixtures
# ============================================================================

@pytest.fixture
def company1_config() -> TenantConfig:
    """Get configuration for Company1 tenant."""
    return Config.get_tenant("company1")


@pytest.fixture
def company2_config() -> TenantConfig:
    """Get configuration for Company2 tenant."""
    return Config.get_tenant("company2")


@pytest.fixture
def company1_page(browser: Browser, company1_config: TenantConfig) -> Generator[Page, None, None]:
    """Create a page logged in as Company1 admin."""
    context = browser.new_context(**Config.get_context_options())
    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)
    
    # Perform login
    page.goto(f"{company1_config.base_url}/login")
    page.wait_for_selector("#email", state="visible")
    page.fill("#email", company1_config.admin_email)
    page.fill("#password", company1_config.admin_password)
    page.click("#login-btn")
    page.wait_for_url("**/dashboard**")
    
    yield page
    
    context.close()


@pytest.fixture
def company2_page(browser: Browser, company2_config: TenantConfig) -> Generator[Page, None, None]:
    """Create a page logged in as Company2 admin."""
    context = browser.new_context(**Config.get_context_options())
    page = context.new_page()
    page.set_default_timeout(Config.DEFAULT_TIMEOUT)
    
    # Perform login
    page.goto(f"{company2_config.base_url}/login")
    page.wait_for_selector("#email", state="visible")
    page.fill("#email", company2_config.admin_email)
    page.fill("#password", company2_config.admin_password)
    page.click("#login-btn")
    page.wait_for_url("**/dashboard**")
    
    yield page
    
    context.close()


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client_company1() -> APIClient:
    """Create an API client for Company1 tenant."""
    headers = auth_manager.get_tenant_auth("company1")
    return APIClient(
        base_url=Config.get_api_base_url(),
        token=headers["Authorization"].replace("Bearer ", ""),
        tenant_id="company1"
    )


@pytest.fixture
def api_client_company2() -> APIClient:
    """Create an API client for Company2 tenant."""
    headers = auth_manager.get_tenant_auth("company2")
    return APIClient(
        base_url=Config.get_api_base_url(),
        token=headers["Authorization"].replace("Bearer ", ""),
        tenant_id="company2"
    )


# ============================================================================
# Test Data Management Fixtures
# ============================================================================

@pytest.fixture
def test_project_data() -> dict:
    """Provide standard test project data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Project {unique_id}",
        "description": "Automated test project",
        "team_members": ["user1@test.com"]
    }


@pytest.fixture
def cleanup_projects(api_client_company1):
    """
    Fixture to track and cleanup created projects after tests.
    
    Usage:
        def test_example(cleanup_projects, api_client_company1):
            project = api_client_company1.create_project(data)
            cleanup_projects.append(project["id"])
    """
    created_project_ids = []
    yield created_project_ids
    
    # Cleanup after test
    for project_id in created_project_ids:
        try:
            api_client_company1.delete_project(project_id)
        except Exception:
            pass  # Ignore cleanup errors


# ============================================================================
# BrowserStack Fixtures (for cross-platform testing)
# ============================================================================

@pytest.fixture(scope="session")
def browserstack_config():
    """Get BrowserStack configuration if available."""
    return Config.get_browserstack_config()


@pytest.fixture
def mobile_ios_page(browserstack_config):
    """
    Create a page for iOS Safari testing via BrowserStack.
    
    Note: This requires valid BrowserStack credentials.
    """
    if not browserstack_config:
        pytest.skip("BrowserStack not configured")
    
    # BrowserStack capabilities for iOS
    capabilities = {
        "browserName": "Safari",
        "device": "iPhone 14",
        "realMobile": "true",
        "os_version": "16",
        "project": browserstack_config.project_name,
        "build": browserstack_config.build_name,
        "name": "iOS Mobile Test",
    }
    
    # For Playwright + BrowserStack, we'd use their CDP endpoint
    # This is a placeholder - actual implementation depends on setup
    pytest.skip("BrowserStack iOS testing requires additional setup")


@pytest.fixture
def mobile_android_page(browserstack_config):
    """
    Create a page for Android Chrome testing via BrowserStack.
    
    Note: This requires valid BrowserStack credentials.
    """
    if not browserstack_config:
        pytest.skip("BrowserStack not configured")
    
    capabilities = {
        "browserName": "Chrome",
        "device": "Samsung Galaxy S23",
        "realMobile": "true",
        "os_version": "13.0",
        "project": browserstack_config.project_name,
        "build": browserstack_config.build_name,
        "name": "Android Mobile Test",
    }
    
    pytest.skip("BrowserStack Android testing requires additional setup")


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "mobile: marks tests requiring mobile device")
    config.addinivalue_line("markers", "browserstack: marks tests requiring BrowserStack")
    config.addinivalue_line("markers", "tenant_isolation: marks tenant isolation security tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers and environment."""
    bs_config = Config.get_browserstack_config()
    
    for item in items:
        # Skip mobile/browserstack tests if not configured
        if "mobile" in item.keywords or "browserstack" in item.keywords:
            if not bs_config:
                item.add_marker(pytest.mark.skip(reason="BrowserStack not configured"))
