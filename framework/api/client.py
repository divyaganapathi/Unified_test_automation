"""HTTP API client with built-in logging, retry, and response wrapping."""

from __future__ import annotations

import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from framework.api.models import APIResponse
from framework.utils.config import Config
from framework.utils.logger import get_logger

logger = get_logger("api.client")


class APIClient:
    """Session-based HTTP client for API testing.

    Features:
    - Automatic base-URL composition
    - Configurable retry strategy (on 5xx and connection errors)
    - Request/response logging
    - Wraps every response in :class:`~framework.api.models.APIResponse`

    Example::

        client = APIClient()
        response = client.get("/users/1")
        assert response.status_code == 200
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        config = Config()
        self._base_url = (base_url or config.api_base_url).rstrip("/")
        self._timeout = timeout or config.api_timeout
        self._session = self._build_session(
            headers={**config.api_headers, **(headers or {})}
        )

    # ------------------------------------------------------------------
    # HTTP verbs
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict[str, Any] | None = None, **kwargs: Any) -> APIResponse:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Any = None, data: Any = None, **kwargs: Any) -> APIResponse:
        return self._request("POST", path, json=json, data=data, **kwargs)

    def put(self, path: str, json: Any = None, **kwargs: Any) -> APIResponse:
        return self._request("PUT", path, json=json, **kwargs)

    def patch(self, path: str, json: Any = None, **kwargs: Any) -> APIResponse:
        return self._request("PATCH", path, json=json, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        return self._request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying requests session."""
        self._session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _request(self, method: str, path: str, **kwargs: Any) -> APIResponse:
        url = self._base_url + "/" + path.lstrip("/")
        kwargs.setdefault("timeout", self._timeout)

        logger.debug("→ %s %s  params=%s  body=%s", method, url, kwargs.get("params"), kwargs.get("json"))
        start = time.monotonic()
        raw = self._session.request(method, url, **kwargs)
        elapsed_ms = (time.monotonic() - start) * 1000

        body = self._parse_body(raw)
        response = APIResponse(
            status_code=raw.status_code,
            headers=dict(raw.headers),
            body=body,
            elapsed_ms=elapsed_ms,
            url=raw.url,
            method=method,
        )
        logger.debug(
            "← %s %s  elapsed=%.1fms  size=%d bytes",
            raw.status_code,
            url,
            elapsed_ms,
            len(raw.content),
        )
        return response

    @staticmethod
    def _parse_body(response: requests.Response) -> Any:
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or "application/javascript" in content_type:
            try:
                return response.json()
            except ValueError:
                pass
        return response.text

    @staticmethod
    def _build_session(headers: dict[str, str]) -> requests.Session:
        session = requests.Session()
        session.headers.update(headers)
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
