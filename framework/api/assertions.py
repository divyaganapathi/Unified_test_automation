"""Fluent assertion helpers for API responses."""

from __future__ import annotations

from typing import Any

from framework.api.models import APIResponse
from framework.utils.logger import get_logger

logger = get_logger("api.assertions")


class APIAssertions:
    """Fluent assertion builder for :class:`~framework.api.models.APIResponse`.

    All methods return ``self`` so that assertions can be chained::

        APIAssertions(response) \\
            .status(200) \\
            .has_key("id") \\
            .key_equals("title", "foo")
    """

    def __init__(self, response: APIResponse) -> None:
        self._response = response

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self, expected: int) -> "APIAssertions":
        """Assert the HTTP status code."""
        actual = self._response.status_code
        assert actual == expected, (
            f"Expected status {expected}, got {actual}. URL={self._response.url}"
        )
        logger.debug("✓ status == %d", expected)
        return self

    def status_ok(self) -> "APIAssertions":
        """Assert any 2xx status code."""
        actual = self._response.status_code
        assert 200 <= actual < 300, (
            f"Expected 2xx status, got {actual}. URL={self._response.url}"
        )
        logger.debug("✓ status is 2xx (%d)", actual)
        return self

    # ------------------------------------------------------------------
    # Response time
    # ------------------------------------------------------------------

    def response_time_under(self, max_ms: float) -> "APIAssertions":
        """Assert the response was received within *max_ms* milliseconds."""
        actual = self._response.elapsed_ms
        assert actual <= max_ms, (
            f"Expected response time ≤ {max_ms}ms, got {actual:.1f}ms"
        )
        logger.debug("✓ response time %.1fms ≤ %sms", actual, max_ms)
        return self

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def body_is_not_empty(self) -> "APIAssertions":
        """Assert the response body is not None/empty."""
        assert self._response.body not in (None, "", [], {}), (
            "Expected non-empty response body"
        )
        return self

    def has_key(self, *keys: str) -> "APIAssertions":
        """Assert that all provided top-level keys exist in the JSON body."""
        body = self._response.body
        assert isinstance(body, dict), f"Response body is not a dict: {type(body)}"
        for key in keys:
            assert key in body, f"Key '{key}' not found in response body. Keys: {list(body.keys())}"
            logger.debug("✓ key '%s' present", key)
        return self

    def key_equals(self, key: str, expected: Any) -> "APIAssertions":
        """Assert that a top-level key equals the expected value."""
        body = self._response.body
        assert isinstance(body, dict), f"Response body is not a dict: {type(body)}"
        actual = body.get(key)
        assert actual == expected, (
            f"Key '{key}': expected {expected!r}, got {actual!r}"
        )
        logger.debug("✓ body['%s'] == %r", key, expected)
        return self

    def body_contains(self, substring: str) -> "APIAssertions":
        """Assert the raw body text contains *substring*."""
        text = str(self._response.body)
        assert substring in text, (
            f"Expected body to contain {substring!r}. Body: {text[:200]}"
        )
        return self

    def is_list(self) -> "APIAssertions":
        """Assert the response body is a JSON array."""
        assert isinstance(self._response.body, list), (
            f"Expected list body, got {type(self._response.body)}"
        )
        return self

    def list_length_at_least(self, min_len: int) -> "APIAssertions":
        """Assert a list body has at least *min_len* items."""
        self.is_list()
        actual = len(self._response.body)
        assert actual >= min_len, f"Expected at least {min_len} items, got {actual}"
        logger.debug("✓ list length %d ≥ %d", actual, min_len)
        return self

    # ------------------------------------------------------------------
    # Headers
    # ------------------------------------------------------------------

    def header_present(self, header_name: str) -> "APIAssertions":
        """Assert a response header is present (case-insensitive)."""
        headers_lower = {k.lower(): v for k, v in self._response.headers.items()}
        assert header_name.lower() in headers_lower, (
            f"Header '{header_name}' not found. Headers: {list(self._response.headers.keys())}"
        )
        return self

    def header_equals(self, header_name: str, expected_value: str) -> "APIAssertions":
        """Assert a response header equals an expected value."""
        headers_lower = {k.lower(): v for k, v in self._response.headers.items()}
        actual = headers_lower.get(header_name.lower())
        assert actual == expected_value, (
            f"Header '{header_name}': expected {expected_value!r}, got {actual!r}"
        )
        return self
