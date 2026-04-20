"""Test data provider backed by Faker and inline fixtures."""

from __future__ import annotations

import random
import string
from typing import Any

try:
    from faker import Faker as _Faker
    _HAS_FAKER = True
except ImportError:
    _HAS_FAKER = False


class DataProvider:
    """Generates and manages test data.

    Uses *Faker* when available, otherwise falls back to built-in helpers.

    Example::

        dp = DataProvider()
        user = dp.user()
        print(user["name"], user["email"])
    """

    def __init__(self, locale: str = "en_US", seed: int | None = None) -> None:
        if _HAS_FAKER:
            self._faker = _Faker(locale)
            if seed is not None:
                _Faker.seed(seed)
        else:
            self._faker = None

    # ------------------------------------------------------------------
    # Common data generators
    # ------------------------------------------------------------------

    def name(self) -> str:
        """Return a random full name."""
        if self._faker:
            return self._faker.name()
        return "Test User"

    def email(self) -> str:
        """Return a random email address."""
        if self._faker:
            return self._faker.email()
        suffix = self._random_string(6)
        return f"test_{suffix}@example.com"

    def phone(self) -> str:
        """Return a random phone number."""
        if self._faker:
            return self._faker.phone_number()
        return "+1-555-000-0000"

    def address(self) -> dict[str, str]:
        """Return a random address dict."""
        if self._faker:
            return {
                "street": self._faker.street_address(),
                "city": self._faker.city(),
                "state": self._faker.state(),
                "zip": self._faker.postcode(),
                "country": self._faker.country(),
            }
        return {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "90001",
            "country": "US",
        }

    def user(self, **overrides: Any) -> dict[str, Any]:
        """Return a complete user payload."""
        data: dict[str, Any] = {
            "name": self.name(),
            "email": self.email(),
            "phone": self.phone(),
            "username": self._faker.user_name() if self._faker else "testuser",
        }
        data.update(overrides)
        return data

    def post(self, user_id: int = 1, **overrides: Any) -> dict[str, Any]:
        """Return a blog-post style payload (matches JSONPlaceholder schema)."""
        data: dict[str, Any] = {
            "userId": user_id,
            "title": self._faker.sentence() if self._faker else "Sample title",
            "body": self._faker.paragraph() if self._faker else "Sample body text.",
        }
        data.update(overrides)
        return data

    def random_int(self, low: int = 1, high: int = 1000) -> int:
        return random.randint(low, high)

    def random_string(self, length: int = 8) -> str:
        return self._random_string(length)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _random_string(length: int) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
