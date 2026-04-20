"""Base page-object model for Playwright-based UI tests."""

from __future__ import annotations

from typing import Any

from framework.utils.config import Config
from framework.utils.logger import get_logger

logger = get_logger("ui.page")

try:
    from playwright.sync_api import Page, Locator, expect
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False
    Page = Locator = Any  # type: ignore[assignment,misc]


class BasePage:
    """Base class for page-object models.

    Inherit from this and define your locators + interactions::

        class LoginPage(BasePage):
            URL = "/login"

            def fill_credentials(self, username: str, password: str) -> None:
                self.page.get_by_label("Username").fill(username)
                self.page.get_by_label("Password").fill(password)
                self.page.get_by_role("button", name="Login").click()
    """

    URL: str = "/"

    def __init__(self, page: "Page") -> None:
        self.page = page
        self._config = Config()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(self, path: str | None = None) -> "BasePage":
        """Navigate to this page's URL (or a custom path)."""
        target = path or self.URL
        logger.info("Navigating to: %s", target)
        self.page.goto(target)
        return self

    def reload(self) -> "BasePage":
        self.page.reload()
        return self

    @property
    def title(self) -> str:
        return self.page.title()

    @property
    def url(self) -> str:
        return self.page.url

    # ------------------------------------------------------------------
    # Interaction helpers
    # ------------------------------------------------------------------

    def click(self, selector: str) -> "BasePage":
        logger.debug("click: %s", selector)
        self.page.locator(selector).click()
        return self

    def fill(self, selector: str, value: str) -> "BasePage":
        logger.debug("fill: %s = %r", selector, value)
        self.page.locator(selector).fill(value)
        return self

    def select_option(self, selector: str, value: str) -> "BasePage":
        self.page.locator(selector).select_option(value)
        return self

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def wait_for_selector(self, selector: str, state: str = "visible") -> "Locator":
        return self.page.locator(selector).wait_for(state=state)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def assert_title_contains(self, text: str) -> "BasePage":
        if _HAS_PLAYWRIGHT:
            expect(self.page).to_have_title(text)
        else:
            assert text in self.page.title(), f"Expected title to contain '{text}'"
        return self

    def assert_url_contains(self, path: str) -> "BasePage":
        assert path in self.page.url, f"Expected URL to contain '{path}', got '{self.page.url}'"
        return self

    def assert_visible(self, selector: str) -> "BasePage":
        assert self.is_visible(selector), f"Expected element to be visible: {selector}"
        return self

    def assert_text(self, selector: str, expected: str) -> "BasePage":
        actual = self.get_text(selector)
        assert actual == expected, f"Text mismatch on '{selector}': expected {expected!r}, got {actual!r}"
        return self

    def assert_text_contains(self, selector: str, substring: str) -> "BasePage":
        actual = self.get_text(selector)
        assert substring in actual, f"Expected '{selector}' text to contain {substring!r}, got {actual!r}"
        return self
