"""Unit tests for framework internals — run without any external services."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from framework.api.assertions import APIAssertions
from framework.api.models import APIResponse
from framework.ai.analyzer import AITestAnalyzer as TestAnalyzer
from framework.ai.generator import AITestGenerator as TestGenerator
from framework.utils.config import Config
from framework.utils.data_provider import DataProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(
    status: int = 200,
    body: object = None,
    headers: dict | None = None,
    elapsed_ms: float = 100.0,
) -> APIResponse:
    return APIResponse(
        status_code=status,
        headers=headers or {"Content-Type": "application/json"},
        body=body if body is not None else {},
        elapsed_ms=elapsed_ms,
        url="https://api.example.com/test",
        method="GET",
    )


# ===========================================================================
# Config
# ===========================================================================

class TestConfig:
    def test_singleton(self) -> None:
        c1 = Config()
        c2 = Config()
        assert c1 is c2

    def test_api_base_url_not_empty(self) -> None:
        assert Config().api_base_url != ""

    def test_api_timeout_is_positive(self) -> None:
        assert Config().api_timeout > 0


# ===========================================================================
# DataProvider
# ===========================================================================

class TestDataProvider:
    def test_name_returns_string(self) -> None:
        dp = DataProvider()
        assert isinstance(dp.name(), str)
        assert len(dp.name()) > 0

    def test_email_contains_at(self) -> None:
        dp = DataProvider()
        assert "@" in dp.email()

    def test_user_has_required_keys(self) -> None:
        dp = DataProvider()
        user = dp.user()
        for key in ("name", "email", "username"):
            assert key in user

    def test_post_has_required_keys(self) -> None:
        dp = DataProvider()
        post = dp.post(user_id=5)
        assert post["userId"] == 5
        assert "title" in post
        assert "body" in post

    def test_overrides_work(self) -> None:
        dp = DataProvider()
        user = dp.user(email="custom@example.com")
        assert user["email"] == "custom@example.com"

    def test_random_int_in_range(self) -> None:
        dp = DataProvider()
        val = dp.random_int(10, 20)
        assert 10 <= val <= 20

    def test_random_string_length(self) -> None:
        dp = DataProvider()
        s = dp.random_string(12)
        assert len(s) == 12


# ===========================================================================
# APIResponse
# ===========================================================================

class TestAPIResponse:
    def test_repr_contains_status(self) -> None:
        r = _make_response(status=201)
        assert "201" in repr(r)

    def test_get_nested_key(self) -> None:
        r = _make_response(body={"data": {"id": 99}})
        assert r.get("data", "id") == 99

    def test_get_missing_key_returns_default(self) -> None:
        r = _make_response(body={"a": 1})
        assert r.get("b", default="missing") == "missing"

    def test_json_returns_body(self) -> None:
        r = _make_response(body={"key": "value"})
        assert r.json() == {"key": "value"}


# ===========================================================================
# APIAssertions
# ===========================================================================

class TestAPIAssertions:
    def test_status_passes(self) -> None:
        APIAssertions(_make_response(status=200)).status(200)

    def test_status_fails_on_mismatch(self) -> None:
        with pytest.raises(AssertionError):
            APIAssertions(_make_response(status=404)).status(200)

    def test_status_ok_passes_for_2xx(self) -> None:
        for code in (200, 201, 204):
            APIAssertions(_make_response(status=code)).status_ok()

    def test_status_ok_fails_for_4xx(self) -> None:
        with pytest.raises(AssertionError):
            APIAssertions(_make_response(status=404)).status_ok()

    def test_has_key_passes(self) -> None:
        r = _make_response(body={"id": 1, "name": "Alice"})
        APIAssertions(r).has_key("id", "name")

    def test_has_key_fails_for_missing(self) -> None:
        r = _make_response(body={"id": 1})
        with pytest.raises(AssertionError):
            APIAssertions(r).has_key("missing")

    def test_key_equals_passes(self) -> None:
        r = _make_response(body={"foo": "bar"})
        APIAssertions(r).key_equals("foo", "bar")

    def test_key_equals_fails_on_wrong_value(self) -> None:
        r = _make_response(body={"foo": "bar"})
        with pytest.raises(AssertionError):
            APIAssertions(r).key_equals("foo", "baz")

    def test_is_list_passes(self) -> None:
        r = _make_response(body=[1, 2, 3])
        APIAssertions(r).is_list()

    def test_is_list_fails_for_dict(self) -> None:
        r = _make_response(body={"a": 1})
        with pytest.raises(AssertionError):
            APIAssertions(r).is_list()

    def test_list_length_at_least_passes(self) -> None:
        r = _make_response(body=[1, 2, 3])
        APIAssertions(r).list_length_at_least(2)

    def test_list_length_at_least_fails(self) -> None:
        r = _make_response(body=[1])
        with pytest.raises(AssertionError):
            APIAssertions(r).list_length_at_least(5)

    def test_response_time_under_passes(self) -> None:
        r = _make_response(elapsed_ms=100)
        APIAssertions(r).response_time_under(500)

    def test_response_time_under_fails(self) -> None:
        r = _make_response(elapsed_ms=600)
        with pytest.raises(AssertionError):
            APIAssertions(r).response_time_under(500)

    def test_body_is_not_empty_passes(self) -> None:
        r = _make_response(body={"a": 1})
        APIAssertions(r).body_is_not_empty()

    def test_body_is_not_empty_fails_on_empty_dict(self) -> None:
        r = _make_response(body={})
        with pytest.raises(AssertionError):
            APIAssertions(r).body_is_not_empty()

    def test_chaining(self) -> None:
        r = _make_response(status=200, body={"id": 1, "name": "Alice"})
        (
            APIAssertions(r)
            .status(200)
            .has_key("id", "name")
            .key_equals("id", 1)
            .response_time_under(5000)
        )

    def test_header_present_passes(self) -> None:
        r = _make_response(headers={"Content-Type": "application/json"})
        APIAssertions(r).header_present("Content-Type")

    def test_header_present_case_insensitive(self) -> None:
        r = _make_response(headers={"content-type": "application/json"})
        APIAssertions(r).header_present("Content-Type")

    def test_header_present_fails_for_missing(self) -> None:
        r = _make_response(headers={})
        with pytest.raises(AssertionError):
            APIAssertions(r).header_present("X-Custom-Header")

    def test_body_contains_passes(self) -> None:
        r = _make_response(body={"message": "Hello World"})
        APIAssertions(r).body_contains("Hello")

    def test_body_contains_fails(self) -> None:
        r = _make_response(body={"message": "Hello World"})
        with pytest.raises(AssertionError):
            APIAssertions(r).body_contains("XYZ_NOT_PRESENT")


# ===========================================================================
# TestGenerator (AI off)
# ===========================================================================

class TestTestGenerator:
    def test_not_available_without_key(self) -> None:
        gen = TestGenerator()
        # In CI without OPENAI_API_KEY the generator should not be available
        # We can't assert the exact state, but we can assert it doesn't raise.
        result = gen.generate_api_tests("GET /users returns a list")
        assert isinstance(result, str)

    def test_generate_returns_string(self) -> None:
        gen = TestGenerator()
        result = gen.generate_ui_tests("Login page with username and password")
        assert isinstance(result, str)


# ===========================================================================
# TestAnalyzer (AI off)
# ===========================================================================

class TestTestAnalyzer:
    def test_analyze_failures_returns_string(self) -> None:
        analyzer = TestAnalyzer()
        failures = [
            {"nodeid": "tests/api/test_foo.py::test_bar", "outcome": "failed", "message": "AssertionError"}
        ]
        result = analyzer.analyze_failures(failures)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_analyze_missing_file_returns_message(self, tmp_path) -> None:
        analyzer = TestAnalyzer()
        result = analyzer.analyze(tmp_path / "nonexistent.json")
        assert "not found" in result.lower()

    def test_analyze_real_report(self, tmp_path) -> None:
        report = {
            "duration": 1.5,
            "summary": {"total": 3, "passed": 2, "failed": 1, "error": 0, "skipped": 0},
            "tests": [
                {"nodeid": "tests/test_a.py::test_pass", "outcome": "passed", "call": {}},
                {"nodeid": "tests/test_a.py::test_pass2", "outcome": "passed", "call": {}},
                {
                    "nodeid": "tests/test_a.py::test_fail",
                    "outcome": "failed",
                    "call": {"longrepr": "AssertionError: expected 200, got 500"},
                },
            ],
        }
        path = tmp_path / "report.json"
        path.write_text(json.dumps(report))
        analyzer = TestAnalyzer()
        result = analyzer.analyze(path)
        assert isinstance(result, str)
        assert len(result) > 0
