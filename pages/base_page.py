"""
Base Page Object Module

Provides a base class for all page objects with common functionality,
proper waits, and error handling.
"""

from playwright.sync_api import Page, Locator, expect, TimeoutError as PlaywrightTimeout
from typing import Optional
from utils.config import Config


class BasePage:
    """
    Base class for all Page Objects.
    
    Provides common functionality:
    - Navigation with waits
    - Element interaction with proper waits
    - Screenshot capture on failure
    - Configurable timeouts
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.DEFAULT_TIMEOUT
        self.element_timeout = Config.ELEMENT_TIMEOUT
    
    # =========================================================================
    # Navigation Methods
    # =========================================================================
    
    def navigate_to(self, url: str) -> None:
        """Navigate to a URL and wait for network idle."""
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
    
    def wait_for_url_pattern(self, pattern: str, timeout: Optional[int] = None) -> None:
        """Wait for URL to match a pattern."""
        self.page.wait_for_url(pattern, timeout=timeout or self.timeout)
    
    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url
    
    def refresh(self) -> None:
        """Refresh the current page."""
        self.page.reload()
        self.page.wait_for_load_state("networkidle")
    
    # =========================================================================
    # Element Interaction Methods
    # =========================================================================
    
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """Click an element with proper wait."""
        self.page.locator(selector).click(timeout=timeout or self.timeout)
    
    def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """Fill a text input with proper wait."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.timeout)
        locator.fill(text)
    
    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get text content of an element."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout or self.timeout)
        return locator.text_content() or ""
    
    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if an element is visible."""
        try:
            expect(self.page.locator(selector)).to_be_visible(
                timeout=timeout or self.element_timeout
            )
            return True
        except (PlaywrightTimeout, AssertionError):
            return False
    
    def wait_for_element(self, selector: str, state: str = "visible", timeout: Optional[int] = None) -> Locator:
        """Wait for an element to be in a specific state."""
        locator = self.page.locator(selector)
        locator.wait_for(state=state, timeout=timeout or self.timeout)
        return locator
    
    def get_all_elements(self, selector: str) -> list:
        """Get all elements matching a selector."""
        self.page.wait_for_load_state("networkidle")
        return self.page.locator(selector).all()
    
    # =========================================================================
    # Assertion Methods
    # =========================================================================
    
    def assert_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """Assert that an element is visible."""
        expect(self.page.locator(selector)).to_be_visible(
            timeout=timeout or self.element_timeout
        )
    
    def assert_text_contains(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """Assert that an element contains specific text."""
        expect(self.page.locator(selector)).to_contain_text(
            text, timeout=timeout or self.element_timeout
        )
    
    def assert_url_contains(self, text: str) -> None:
        """Assert that the current URL contains specific text."""
        assert text in self.page.url, f"Expected URL to contain '{text}', got '{self.page.url}'"
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def take_screenshot(self, name: str) -> str:
        """Take a screenshot and return the path."""
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path)
        return path
    
    def wait_for_network_idle(self) -> None:
        """Wait for network activity to settle."""
        self.page.wait_for_load_state("networkidle")
    
    def scroll_to_element(self, selector: str) -> None:
        """Scroll an element into view."""
        self.page.locator(selector).scroll_into_view_if_needed()
