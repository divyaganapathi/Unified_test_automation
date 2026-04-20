"""Playwright browser/context/page lifecycle manager."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from framework.utils.config import Config
from framework.utils.logger import get_logger

logger = get_logger("ui.driver")

try:
    from playwright.sync_api import (
        Browser,
        BrowserContext,
        Page,
        Playwright,
        sync_playwright,
    )
    _HAS_PLAYWRIGHT = True
except ImportError:
    _HAS_PLAYWRIGHT = False
    Browser = BrowserContext = Page = Playwright = Any  # type: ignore[assignment,misc]


class BrowserManager:
    """Manages Playwright browser, context and page lifecycle.

    Usage in a pytest fixture::

        @pytest.fixture
        def page():
            with BrowserManager() as mgr:
                yield mgr.new_page()

    or manually::

        mgr = BrowserManager()
        mgr.start()
        page = mgr.new_page()
        ...
        mgr.stop()
    """

    def __init__(
        self,
        browser_type: str | None = None,
        headless: bool | None = None,
        base_url: str | None = None,
        viewport: dict[str, int] | None = None,
    ) -> None:
        if not _HAS_PLAYWRIGHT:
            raise ImportError(
                "playwright is not installed. Run: pip install playwright && playwright install"
            )

        config = Config()
        self._browser_type = browser_type or config.browser
        self._headless = headless if headless is not None else config.headless
        self._base_url = base_url or config.ui_base_url
        self._viewport = viewport or config.viewport
        self._timeout = config.ui_timeout
        self._screenshot_on_failure = config.screenshot_on_failure

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Launch the browser."""
        logger.info("Starting browser: %s (headless=%s)", self._browser_type, self._headless)
        self._playwright = sync_playwright().start()
        launcher = getattr(self._playwright, self._browser_type)
        self._browser = launcher.launch(headless=self._headless)
        self._context = self._browser.new_context(
            base_url=self._base_url or None,
            viewport=self._viewport,
            record_video_dir=self._video_dir() if self._should_record_video() else None,
        )
        self._context.set_default_timeout(self._timeout)
        logger.info("Browser started")

    def stop(self, failed: bool = False) -> None:
        """Close the browser and save artefacts on failure."""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        logger.info("Browser stopped")

    def new_page(self) -> "Page":
        """Return a new page in the managed context."""
        if self._context is None:
            self.start()
        page = self._context.new_page()  # type: ignore[union-attr]
        return page

    def take_screenshot(self, page: "Page", name: str = "screenshot") -> Path:
        """Capture a screenshot and save it to the reports directory."""
        config = Config()
        shots_dir = config.report_dir / "screenshots"
        shots_dir.mkdir(parents=True, exist_ok=True)
        path = shots_dir / f"{name}.png"
        page.screenshot(path=str(path))
        logger.info("Screenshot saved: %s", path)
        return path

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "BrowserManager":
        self.start()
        return self

    def __exit__(self, exc_type: Any, *_: Any) -> None:
        self.stop(failed=exc_type is not None)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _video_dir(self) -> str:
        config = Config()
        video_dir = config.report_dir / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        return str(video_dir)

    def _should_record_video(self) -> bool:
        config = Config()
        return bool(config.get("ui", "video_on_failure", default=False))
