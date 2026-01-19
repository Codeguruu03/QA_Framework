"""
Login Page Object

Handles login functionality with proper waits and error handling.
Inherits from BasePage for common functionality.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from utils.config import Config


class LoginPage(BasePage):
    """
    Page Object for the login page.
    
    Selectors:
    - #email: Email input field
    - #password: Password input field
    - #login-btn: Login submit button
    - .error-message: Error message display
    - .welcome-message: Success message on dashboard
    """
    
    # Selectors
    EMAIL_INPUT = "#email"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-btn"
    ERROR_MESSAGE = ".error-message"
    TWO_FA_INPUT = "#two-fa-code"
    TWO_FA_SUBMIT = "#two-fa-submit"
    
    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page)
        self.base_url = base_url or "https://app.workflowpro.com"
    
    def navigate_to_login(self) -> None:
        """Navigate to the login page."""
        self.navigate_to(f"{self.base_url}/login")
        self.wait_for_element(self.EMAIL_INPUT, state="visible")
    
    def login(self, email: str, password: str) -> None:
        """
        Perform login with email and password.
        
        Args:
            email: User email address
            password: User password
        """
        self.navigate_to_login()
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
    
    def login_with_2fa(self, email: str, password: str, code: str) -> None:
        """
        Perform login with 2FA code.
        
        Args:
            email: User email address
            password: User password
            code: Two-factor authentication code
        """
        self.login(email, password)
        
        # Wait for 2FA prompt
        if self.is_visible(self.TWO_FA_INPUT, timeout=5000):
            self.fill(self.TWO_FA_INPUT, code)
            self.click(self.TWO_FA_SUBMIT)
    
    def is_login_successful(self) -> bool:
        """Check if login was successful by verifying dashboard URL."""
        try:
            self.wait_for_url_pattern("**/dashboard**", timeout=Config.DEFAULT_TIMEOUT)
            return True
        except Exception:
            return False
    
    def get_error_message(self) -> str:
        """Get the login error message if present."""
        if self.is_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def assert_login_error(self, expected_text: str = None) -> None:
        """Assert that a login error is displayed."""
        self.assert_visible(self.ERROR_MESSAGE)
        if expected_text:
            self.assert_text_contains(self.ERROR_MESSAGE, expected_text)
