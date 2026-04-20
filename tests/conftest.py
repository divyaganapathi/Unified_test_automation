"""Shared pytest fixtures for API and UI tests."""

from __future__ import annotations

import pytest

from framework.api import APIClient
from framework.utils.config import Config
from framework.utils.data_provider import DataProvider
from framework.utils.logger import get_logger

logger = get_logger("conftest")


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def config() -> Config:
    """Provide the global Config singleton."""
    return Config()


@pytest.fixture(scope="session")
def data() -> DataProvider:
    """Provide a DataProvider instance for the whole session."""
    return DataProvider()


# ---------------------------------------------------------------------------
# API fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_client(config: Config) -> APIClient:
    """Return a session-scoped APIClient and close it after the session."""
    client = APIClient(base_url=config.api_base_url)
    yield client
    client.close()


# ---------------------------------------------------------------------------
# UI fixtures (only created when playwright is installed)
# ---------------------------------------------------------------------------

def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


if _playwright_available():
    from framework.ui.driver import BrowserManager

    @pytest.fixture(scope="session")
    def browser_manager(config: Config):
        """Session-scoped browser manager (single browser instance per run)."""
        mgr = BrowserManager(
            browser_type=config.browser,
            headless=config.headless,
            base_url=config.ui_base_url,
        )
        mgr.start()
        yield mgr
        mgr.stop()

    @pytest.fixture
    def page(browser_manager: "BrowserManager"):
        """Fresh page for each test function."""
        p = browser_manager.new_page()
        yield p
        p.close()

else:
    logger.warning(
        "playwright not installed — UI fixtures unavailable. "
        "Run: pip install playwright && playwright install"
    )
