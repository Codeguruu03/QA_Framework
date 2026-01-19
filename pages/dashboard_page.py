"""
Dashboard Page Object

Handles dashboard functionality including project visibility,
navigation, and tenant-specific content verification.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from typing import List, Optional


class DashboardPage(BasePage):
    """
    Page Object for the dashboard page.
    
    Selectors:
    - .welcome-message: Welcome message after login
    - .project-card: Individual project cards
    - .projects-container: Container for all projects
    - .create-project-btn: Button to create new project
    """
    
    # Selectors
    WELCOME_MESSAGE = ".welcome-message"
    PROJECT_CARD = ".project-card"
    PROJECTS_CONTAINER = ".projects-container"
    CREATE_PROJECT_BTN = ".create-project-btn"
    PROJECT_NAME_SELECTOR = ".project-name"
    PROJECT_STATUS = ".project-status"
    SIDEBAR = ".sidebar"
    LOGOUT_BTN = "#logout-btn"
    
    def __init__(self, page: Page):
        super().__init__(page)
    
    def wait_for_dashboard(self, timeout: Optional[int] = None) -> None:
        """Wait for dashboard to fully load."""
        self.wait_for_url_pattern("**/dashboard**", timeout=timeout)
        self.wait_for_network_idle()
    
    def is_dashboard_loaded(self) -> bool:
        """Check if the dashboard has loaded successfully."""
        try:
            self.wait_for_dashboard(timeout=5000)
            return True
        except Exception:
            return False
    
    def is_welcome_message_visible(self) -> bool:
        """Check if the welcome message is visible."""
        return self.is_visible(self.WELCOME_MESSAGE)
    
    def get_welcome_message(self) -> str:
        """Get the welcome message text."""
        if self.is_welcome_message_visible():
            return self.get_text(self.WELCOME_MESSAGE)
        return ""
    
    # =========================================================================
    # Project Methods
    # =========================================================================
    
    def is_project_visible(self, project_name: str) -> bool:
        """
        Check if a specific project is visible on the dashboard.
        
        Args:
            project_name: Name of the project to find
            
        Returns:
            True if project is visible, False otherwise
        """
        # Wait for projects to load
        self.wait_for_network_idle()
        
        # Look for project by name
        project_locator = self.page.locator(f"{self.PROJECT_CARD}:has-text('{project_name}')")
        return project_locator.count() > 0
    
    def get_all_project_names(self) -> List[str]:
        """Get names of all visible projects."""
        self.wait_for_network_idle()
        
        # Small wait for JS rendering
        self.page.wait_for_timeout(500)
        
        project_cards = self.page.locator(self.PROJECT_CARD).all()
        names = []
        for card in project_cards:
            name_element = card.locator(self.PROJECT_NAME_SELECTOR)
            if name_element.count() > 0:
                names.append(name_element.text_content() or "")
            else:
                names.append(card.text_content() or "")
        return names
    
    def get_project_count(self) -> int:
        """Get the total number of visible projects."""
        self.wait_for_network_idle()
        return self.page.locator(self.PROJECT_CARD).count()
    
    def click_project(self, project_name: str) -> None:
        """Click on a project card to open it."""
        project_card = self.page.locator(f"{self.PROJECT_CARD}:has-text('{project_name}')")
        project_card.click()
    
    def click_create_project(self) -> None:
        """Click the create project button."""
        self.click(self.CREATE_PROJECT_BTN)
    
    # =========================================================================
    # Tenant Isolation Methods
    # =========================================================================
    
    def verify_no_cross_tenant_data(self, excluded_tenant: str) -> bool:
        """
        Verify that no data from another tenant is visible.
        
        Args:
            excluded_tenant: Tenant name that should NOT appear
            
        Returns:
            True if no cross-tenant data found, False otherwise
        """
        self.wait_for_network_idle()
        
        project_cards = self.page.locator(self.PROJECT_CARD).all()
        for card in project_cards:
            text = card.text_content() or ""
            if excluded_tenant in text:
                return False
        return True
    
    # =========================================================================
    # Navigation Methods
    # =========================================================================
    
    def logout(self) -> None:
        """Log out of the application."""
        self.click(self.LOGOUT_BTN)
        self.wait_for_url_pattern("**/login**")
    
    def navigate_to_settings(self) -> None:
        """Navigate to settings page."""
        self.click(".settings-link")
        self.wait_for_url_pattern("**/settings**")
