"""
Part 1: Debugging Flaky Test Code - Fixed Version

Original Issues Identified:
1. No headless mode - fails in CI/CD environments without display
2. Direct URL assertion - fails with redirects, query params, or timing issues  
3. No explicit waits - race conditions with dynamic content
4. No timeout configuration - default timeouts may be too short
5. No browser close in error cases - resource leaks
6. No retry mechanism for network flakiness

Root Causes (CI/CD vs Local):
- CI runs headless, local may have display
- CI has different network latency
- CI runs on various browsers/screen sizes
- CI may have stricter resource constraints
- Dynamic content loads at different speeds
"""

import pytest
from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout


class TestUserLogin:
    """Test class for user login functionality with proper reliability fixes."""
    
    # Configuration constants
    BASE_URL = "https://app.workflowpro.com"
    DEFAULT_TIMEOUT = 15000  # 15 seconds for slow CI environments
    ELEMENT_TIMEOUT = 10000  # 10 seconds for element visibility
    
    def test_user_login_successful(self):
        """
        Test: Verify successful user login flow.
        
        Fixes Applied:
        - headless=True for CI compatibility
        - wait_for_url with pattern matching (handles redirects)
        - expect() with timeout for element visibility
        - Proper browser cleanup in try/finally
        """
        with sync_playwright() as p:
            browser = None
            try:
                # ✅ FIX 1: Headless mode for CI/CD
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # ✅ FIX 2: Set default timeout for all operations
                page.set_default_timeout(self.DEFAULT_TIMEOUT)
                
                # Navigate to login page
                page.goto(f"{self.BASE_URL}/login")
                
                # ✅ FIX 3: Wait for form elements before interacting
                page.wait_for_selector("#email", state="visible")
                
                # Fill login form
                page.fill("#email", "admin@company1.com")
                page.fill("#password", "password123")
                page.click("#login-btn")
                
                # ✅ FIX 4: Pattern matching for URL (handles query params, redirects)
                page.wait_for_url("**/dashboard**", timeout=self.DEFAULT_TIMEOUT)
                
                # ✅ FIX 5: Explicit wait with Playwright's expect API
                expect(page.locator(".welcome-message")).to_be_visible(
                    timeout=self.ELEMENT_TIMEOUT
                )
                
            except PlaywrightTimeout as e:
                pytest.fail(f"Login test timed out: {e}")
            finally:
                # ✅ FIX 6: Always clean up browser resources
                if browser:
                    browser.close()

    def test_user_login_invalid_credentials(self):
        """Test: Verify error message for invalid login credentials."""
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(self.DEFAULT_TIMEOUT)
                
                page.goto(f"{self.BASE_URL}/login")
                page.wait_for_selector("#email", state="visible")
                
                # Enter invalid credentials
                page.fill("#email", "invalid@company1.com")
                page.fill("#password", "wrongpassword")
                page.click("#login-btn")
                
                # Should show error message, not redirect
                expect(page.locator(".error-message")).to_be_visible(
                    timeout=self.ELEMENT_TIMEOUT
                )
                
                # Should stay on login page
                expect(page).to_have_url(f"{self.BASE_URL}/login")
                
            finally:
                if browser:
                    browser.close()


class TestMultiTenantAccess:
    """
    Test class for multi-tenant isolation verification.
    
    Original Issues:
    1. No waits for dynamic project loading
    2. Race condition with .all() on loading elements
    3. No handling for empty project list
    4. Direct text_content() without waiting
    """
    
    BASE_URL = "https://app.workflowpro.com"
    DEFAULT_TIMEOUT = 15000
    ELEMENT_TIMEOUT = 10000
    
    def test_multi_tenant_access_company2(self):
        """
        Test: Verify Company2 user only sees Company2 data.
        
        Fixes Applied:
        - Wait for dashboard to fully load
        - Wait for project cards to be rendered
        - Handle empty state gracefully
        - Proper assertions with timeout
        """
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(self.DEFAULT_TIMEOUT)
                
                # Login flow
                page.goto(f"{self.BASE_URL}/login")
                page.wait_for_selector("#email", state="visible")
                page.fill("#email", "user@company2.com")
                page.fill("#password", "password123")
                page.click("#login-btn")
                
                # ✅ FIX 1: Wait for dashboard URL
                page.wait_for_url("**/dashboard**", timeout=self.DEFAULT_TIMEOUT)
                
                # ✅ FIX 2: Wait for page to be fully loaded
                page.wait_for_load_state("networkidle")
                
                # ✅ FIX 3: Wait for project container to exist
                project_container = page.locator(".projects-container")
                expect(project_container).to_be_visible(timeout=self.ELEMENT_TIMEOUT)
                
                # ✅ FIX 4: Wait for project cards to render (or empty state)
                # Allow time for dynamic content
                page.wait_for_timeout(1000)  # Small buffer for JS rendering
                
                projects = page.locator(".project-card").all()
                
                # ✅ FIX 5: Handle empty project list gracefully
                if len(projects) == 0:
                    # This is valid - user might have no projects
                    return
                
                # ✅ FIX 6: Verify each project belongs to Company2
                for project in projects:
                    # Wait for text content to be available
                    project.wait_for(state="visible")
                    text_content = project.text_content() or ""
                    
                    # Tenant isolation check
                    assert "Company2" in text_content, (
                        f"Tenant isolation violation: Found non-Company2 project: {text_content}"
                    )
                    
            except PlaywrightTimeout as e:
                pytest.fail(f"Multi-tenant test timed out: {e}")
            finally:
                if browser:
                    browser.close()

    def test_tenant_data_isolation(self):
        """
        Test: Verify Company1 user cannot see Company2 projects.
        
        This is a security-critical test for multi-tenant SaaS.
        """
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(self.DEFAULT_TIMEOUT)
                
                # Login as Company1 user
                page.goto(f"{self.BASE_URL}/login")
                page.wait_for_selector("#email", state="visible")
                page.fill("#email", "admin@company1.com")
                page.fill("#password", "password123")
                page.click("#login-btn")
                
                page.wait_for_url("**/dashboard**", timeout=self.DEFAULT_TIMEOUT)
                page.wait_for_load_state("networkidle")
                
                # Get all visible project cards
                page.wait_for_timeout(1000)
                projects = page.locator(".project-card").all()
                
                # Verify NO Company2 data is visible
                for project in projects:
                    project.wait_for(state="visible")
                    text_content = project.text_content() or ""
                    
                    assert "Company2" not in text_content, (
                        f"SECURITY VIOLATION: Company1 user can see Company2 data: {text_content}"
                    )
                    
            finally:
                if browser:
                    browser.close()
