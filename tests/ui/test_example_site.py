"""Sample UI tests against https://playwright.dev/python/docs/intro (demo site).

These tests demonstrate the framework's UI testing capabilities using
the Playwright-based page-object model.

Note: These tests are skipped automatically when Playwright is not installed.
"""

from __future__ import annotations

import pytest

try:
    from playwright.sync_api import Page, expect
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False

from framework.ui.page import BasePage

pytestmark = pytest.mark.skipif(
    not _HAS_PLAYWRIGHT,
    reason="playwright not installed — run: pip install playwright && playwright install",
)


# ===========================================================================
# Example.com smoke tests
# ===========================================================================

class ExamplePage(BasePage):
    """Minimal page object for https://example.com."""
    URL = "https://example.com"


class TestExampleCom:
    """Basic smoke tests against example.com (always reachable)."""

    @pytest.mark.ui
    @pytest.mark.smoke
    def test_page_title(self, page: "Page") -> None:
        ep = ExamplePage(page)
        ep.navigate()
        assert "Example" in ep.title

    @pytest.mark.ui
    def test_page_has_heading(self, page: "Page") -> None:
        ep = ExamplePage(page)
        ep.navigate()
        ep.assert_visible("h1")

    @pytest.mark.ui
    def test_heading_text(self, page: "Page") -> None:
        ep = ExamplePage(page)
        ep.navigate()
        ep.assert_text_contains("h1", "Example")

    @pytest.mark.ui
    def test_page_has_more_info_link(self, page: "Page") -> None:
        ep = ExamplePage(page)
        ep.navigate()
        ep.assert_visible("a")

    @pytest.mark.ui
    def test_url_after_navigation(self, page: "Page") -> None:
        ep = ExamplePage(page)
        ep.navigate()
        ep.assert_url_contains("example.com")
