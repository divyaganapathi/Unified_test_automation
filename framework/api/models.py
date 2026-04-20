"""Response model and request builder for the API module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class APIResponse:
    """Wraps a raw ``requests.Response`` and exposes convenience attributes."""

    status_code: int
    headers: dict[str, str]
    body: Any                    # parsed JSON or raw text
    elapsed_ms: float            # round-trip time in milliseconds
    url: str
    method: str

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def json(self) -> Any:
        """Return the parsed JSON body (same as ``.body`` when JSON was returned)."""
        return self.body

    def get(self, *keys: str, default: Any = None) -> Any:
        """Navigate nested JSON body with a key path.

        Example::

            response.get("data", "id")   # equivalent to response.body["data"]["id"]
        """
        node: Any = self.body
        for key in keys:
            if isinstance(node, dict):
                node = node.get(key, default)
            elif isinstance(node, list) and isinstance(key, int):
                try:
                    node = node[key]
                except IndexError:
                    return default
            else:
                return default
        return node

    def __repr__(self) -> str:
        return (
            f"APIResponse(status={self.status_code}, "
            f"method={self.method}, "
            f"url={self.url}, "
            f"elapsed={self.elapsed_ms:.1f}ms)"
        )


@dataclass
class RequestSpec:
    """Specification for an outgoing HTTP request."""

    method: str
    path: str
    params: dict[str, Any] = field(default_factory=dict)
    json: Any = None
    data: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    timeout: int = 30
