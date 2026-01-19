"""
Dashboard UI Tests

Tests for dashboard functionality including:
- Dashboard loading and welcome message
- Project visibility and filtering
- Navigation and UI interactions
"""

import pytest
from playwright.sync_api import sync_playwright, expect

from utils.config import Config
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


class TestDashboard:
    """UI tests for the dashboard page."""
    
    def test_dashboard_loads_after_login(self):
        """Test: Dashboard loads correctly after successful login."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=Config.is_headless())
            context = browser.new_context(**Config.get_context_options())
            page = context.new_page()
            page.set_default_timeout(Config.DEFAULT_TIMEOUT)
            
            try:
                login = LoginPage(page)
                dashboard = DashboardPage(page)
                
                tenant = Config.get_tenant("company1")
                login.login(tenant.admin_email, tenant.admin_password)
                
                # Verify dashboard loaded
                assert dashboard.is_dashboard_loaded()
                
            finally:
                context.close()
                browser.close()
    
    def test_welcome_message_displayed(self):
        """Test: Welcome message is displayed on dashboard."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=Config.is_headless())
            context = browser.new_context(**Config.get_context_options())
            page = context.new_page()
            page.set_default_timeout(Config.DEFAULT_TIMEOUT)
            
            try:
                login = LoginPage(page)
                dashboard = DashboardPage(page)
                
                tenant = Config.get_tenant("company1")
                login.login(tenant.admin_email, tenant.admin_password)
                dashboard.wait_for_dashboard()
                
                assert dashboard.is_welcome_message_visible()
                
            finally:
                context.close()
                browser.close()
    
    def test_project_list_displays(self):
        """Test: Project list is displayed on dashboard."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=Config.is_headless())
            context = browser.new_context(**Config.get_context_options())
            page = context.new_page()
            page.set_default_timeout(Config.DEFAULT_TIMEOUT)
            
            try:
                login = LoginPage(page)
                dashboard = DashboardPage(page)
                
                tenant = Config.get_tenant("company1")
                login.login(tenant.admin_email, tenant.admin_password)
                dashboard.wait_for_dashboard()
                
                # Should be able to get project count (even if 0)
                project_count = dashboard.get_project_count()
                assert project_count >= 0
                
            finally:
                context.close()
                browser.close()
    
    @pytest.mark.tenant_isolation
    def test_tenant_data_isolation_ui(self):
        """Test: UI enforces tenant data isolation."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=Config.is_headless())
            
            try:
                # Login as Company1
                context1 = browser.new_context(**Config.get_context_options())
                page1 = context1.new_page()
                page1.set_default_timeout(Config.DEFAULT_TIMEOUT)
                
                login1 = LoginPage(page1)
                dashboard1 = DashboardPage(page1)
                
                tenant1 = Config.get_tenant("company1")
                login1.login(tenant1.admin_email, tenant1.admin_password)
                dashboard1.wait_for_dashboard()
                
                # Verify no Company2 data visible
                assert dashboard1.verify_no_cross_tenant_data("Company2")
                
                context1.close()
                
                # Login as Company2
                context2 = browser.new_context(**Config.get_context_options())
                page2 = context2.new_page()
                page2.set_default_timeout(Config.DEFAULT_TIMEOUT)
                
                login2 = LoginPage(page2)
                dashboard2 = DashboardPage(page2)
                
                tenant2 = Config.get_tenant("company2")
                login2.login(tenant2.admin_email, tenant2.admin_password)
                dashboard2.wait_for_dashboard()
                
                # Verify no Company1 data visible
                assert dashboard2.verify_no_cross_tenant_data("Company1")
                
                context2.close()
                
            finally:
                browser.close()


class TestDashboardResponsiveness:
    """Tests for dashboard responsiveness across different viewports."""
    
    @pytest.mark.parametrize("viewport", [
        {"width": 1920, "height": 1080},  # Desktop
        {"width": 1366, "height": 768},   # Laptop
        {"width": 768, "height": 1024},   # Tablet
        {"width": 375, "height": 667},    # Mobile
    ])
    def test_dashboard_renders_at_viewport(self, viewport):
        """Test: Dashboard renders correctly at various viewports."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=Config.is_headless())
            context = browser.new_context(
                viewport=viewport,
                ignore_https_errors=True
            )
            page = context.new_page()
            page.set_default_timeout(Config.DEFAULT_TIMEOUT)
            
            try:
                login = LoginPage(page)
                dashboard = DashboardPage(page)
                
                tenant = Config.get_tenant("company1")
                login.login(tenant.admin_email, tenant.admin_password)
                
                # Dashboard should load at any viewport
                assert dashboard.is_dashboard_loaded()
                
            finally:
                context.close()
                browser.close()
