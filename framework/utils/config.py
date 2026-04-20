"""Configuration loader.

Reads config/config.yaml and allows environment-variable overrides via .env.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_PATH = _ROOT / "config" / "config.yaml"


class Config:
    """Singleton configuration object backed by config.yaml + environment variables."""

    _instance: "Config | None" = None
    _data: dict[str, Any] = {}

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get(self, *keys: str, default: Any = None) -> Any:
        """Retrieve a nested config value by dotted key path, e.g. ``get('api', 'timeout')``."""
        node: Any = self._data
        for key in keys:
            if not isinstance(node, dict):
                return default
            if key not in node:
                return default
            node = node[key]
        return node

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def api_base_url(self) -> str:
        return os.getenv("API_BASE_URL", self.get("api", "base_url", default=""))

    @property
    def api_timeout(self) -> int:
        return int(os.getenv("API_TIMEOUT", self.get("api", "timeout", default=30)))

    @property
    def api_headers(self) -> dict[str, str]:
        return self.get("api", "headers", default={})

    @property
    def ui_base_url(self) -> str:
        return os.getenv("UI_BASE_URL", self.get("ui", "base_url", default=""))

    @property
    def browser(self) -> str:
        return os.getenv("BROWSER", self.get("ui", "browser", default="chromium"))

    @property
    def headless(self) -> bool:
        val = os.getenv("HEADLESS", str(self.get("ui", "headless", default=True)))
        return val.lower() not in ("false", "0", "no")

    @property
    def viewport(self) -> dict[str, int]:
        return self.get("ui", "viewport", default={"width": 1280, "height": 720})

    @property
    def ui_timeout(self) -> int:
        return int(os.getenv("UI_TIMEOUT", self.get("ui", "timeout", default=30000)))

    @property
    def screenshot_on_failure(self) -> bool:
        return bool(self.get("ui", "screenshot_on_failure", default=True))

    @property
    def ai_model(self) -> str:
        return os.getenv("AI_MODEL", self.get("ai", "model", default="gpt-4o-mini"))

    @property
    def ai_max_tokens(self) -> int:
        return int(os.getenv("AI_MAX_TOKENS", self.get("ai", "max_tokens", default=2048)))

    @property
    def ai_enabled(self) -> bool:
        return bool(self.get("ai", "enabled", default=True))

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", self.get("log_level", default="INFO")).upper()

    @property
    def report_dir(self) -> Path:
        return _ROOT / os.getenv("REPORT_DIR", self.get("report_dir", default="reports"))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if _CONFIG_PATH.exists():
            with _CONFIG_PATH.open() as fh:
                self._data = yaml.safe_load(fh) or {}
        else:
            self._data = {}
