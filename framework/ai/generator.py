"""AI-powered test generator.

Uses the OpenAI chat completions API to generate pytest test skeletons
from an OpenAPI spec, a cURL example, or a plain-English description.

When ``OPENAI_API_KEY`` is not set (or the ``openai`` package is absent),
all methods return an empty list so that the rest of the framework
continues working without AI features.
"""

from __future__ import annotations

import os
from typing import Any

from framework.utils.config import Config
from framework.utils.logger import get_logger

logger = get_logger("ai.generator")

try:
    from openai import OpenAI as _OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

_SYSTEM_PROMPT = """\
You are an expert test automation engineer specializing in Python + pytest.
Generate concise, runnable pytest test functions. Use the framework helpers:
- APIClient (for API tests)
- APIAssertions (for API assertions)
- BasePage / page-object subclasses (for UI tests)
Return only Python code, no explanations.
"""

_API_TEST_PROMPT = """\
Generate pytest test functions for the following API endpoint description:

{description}

Requirements:
- Use `from framework.api import APIClient, APIAssertions`
- Each function name starts with `test_`
- Cover: happy path, missing required field, unauthorized (if applicable)
- Use markers: @pytest.mark.api
"""

_UI_TEST_PROMPT = """\
Generate pytest test functions for the following UI page / feature:

{description}

Requirements:
- Use `from framework.ui import BasePage`
- Each function name starts with `test_`
- Cover: happy path, invalid input
- Use markers: @pytest.mark.ui
- Fixtures: `page` (Playwright Page object)
"""


class AITestGenerator:
    """Generates test code using an LLM.

    Example::

        gen = TestGenerator()
        code = gen.generate_api_tests("GET /users/{id} returns a user object")
        print(code)
    """

    def __init__(self) -> None:
        self._config = Config()
        self._client: Any = None
        if _HAS_OPENAI and self._config.ai_enabled:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                self._client = _OpenAI(api_key=api_key)
            else:
                logger.warning(
                    "OPENAI_API_KEY not set — AI test generation disabled. "
                    "Set the key in .env to enable it."
                )

    @property
    def is_available(self) -> bool:
        """``True`` when AI generation is configured and ready."""
        return self._client is not None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_api_tests(self, description: str) -> str:
        """Return Python source code with pytest test functions for an API endpoint.

        Parameters
        ----------
        description:
            Plain-English or OpenAPI-snippet description of the endpoint.

        Returns
        -------
        str
            Generated Python source, or an empty string when AI is unavailable.
        """
        if not self.is_available:
            logger.info("AI unavailable — skipping API test generation")
            return ""
        prompt = _API_TEST_PROMPT.format(description=description)
        return self._call_llm(prompt)

    def generate_ui_tests(self, description: str) -> str:
        """Return Python source code with pytest test functions for a UI page.

        Parameters
        ----------
        description:
            Plain-English description of the page and actions to test.

        Returns
        -------
        str
            Generated Python source, or an empty string when AI is unavailable.
        """
        if not self.is_available:
            logger.info("AI unavailable — skipping UI test generation")
            return ""
        prompt = _UI_TEST_PROMPT.format(description=description)
        return self._call_llm(prompt)

    def generate_from_custom_prompt(self, prompt: str) -> str:
        """Call the LLM with a fully custom prompt."""
        if not self.is_available:
            return ""
        return self._call_llm(prompt)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._config.ai_model,
                max_tokens=self._config.ai_max_tokens,
                temperature=self._config.get("ai", "temperature", default=0.2),
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            content: str = response.choices[0].message.content or ""
            # Strip markdown fences if the model wrapped the code
            if content.startswith("```"):
                lines = content.splitlines()
                lines = [l for l in lines if not l.startswith("```")]
                content = "\n".join(lines)
            logger.info("AI generated %d chars of test code", len(content))
            return content.strip()
        except Exception as exc:  # pragma: no cover
            logger.error("LLM call failed: %s", exc)
            return ""
