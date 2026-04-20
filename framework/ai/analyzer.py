"""AI-powered test result analyzer.

Reads pytest JSON reports and uses an LLM to:
- Summarise failures in plain English
- Suggest root causes
- Recommend follow-up actions

When AI is unavailable, a basic rule-based summary is returned instead.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from framework.utils.config import Config
from framework.utils.logger import get_logger

logger = get_logger("ai.analyzer")

try:
    from openai import OpenAI as _OpenAI
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

_ANALYSIS_PROMPT = """\
You are a senior QA engineer reviewing automated test results.

Test run summary:
- Total tests  : {total}
- Passed       : {passed}
- Failed       : {failed}
- Errors       : {errors}
- Skipped      : {skipped}
- Duration     : {duration:.1f}s

Failed / errored tests:
{failures}

Provide:
1. A brief (3-5 sentence) summary of what went wrong.
2. Likely root causes grouped by category (network, data, logic, environment).
3. Recommended next steps.

Be concise and actionable.
"""


class AITestAnalyzer:
    """Analyzes pytest JSON reports and produces human-readable summaries.

    Example::

        analyzer = TestAnalyzer()
        report = analyzer.analyze("reports/report.json")
        print(report)
    """

    def __init__(self) -> None:
        self._config = Config()
        self._client: Any = None
        if _HAS_OPENAI and self._config.ai_enabled:
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                self._client = _OpenAI(api_key=api_key)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, report_path: str | Path) -> str:
        """Analyze a pytest JSON report and return a plain-English summary.

        Parameters
        ----------
        report_path:
            Path to the ``--json-report`` output file.

        Returns
        -------
        str
            Human-readable analysis.
        """
        report_path = Path(report_path)
        if not report_path.exists():
            return f"Report file not found: {report_path}"

        with report_path.open() as fh:
            data = json.load(fh)

        summary = self._extract_summary(data)
        if self.is_available:
            return self._ai_analysis(summary)
        return self._rule_based_analysis(summary)

    def analyze_failures(self, failures: list[dict[str, Any]]) -> str:
        """Analyze a list of failure dicts directly (without a report file)."""
        summary = {
            "total": len(failures),
            "passed": 0,
            "failed": len(failures),
            "errors": 0,
            "skipped": 0,
            "duration": 0.0,
            "failure_details": failures,
        }
        if self.is_available:
            return self._ai_analysis(summary)
        return self._rule_based_analysis(summary)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _extract_summary(self, data: dict[str, Any]) -> dict[str, Any]:
        summary = data.get("summary", {})
        tests = data.get("tests", [])
        failures = []
        for test in tests:
            outcome = test.get("outcome", "")
            if outcome in ("failed", "error"):
                failures.append({
                    "nodeid": test.get("nodeid", ""),
                    "outcome": outcome,
                    "message": (test.get("call", {}) or {}).get("longrepr", "")[:500],
                })
        return {
            "total": summary.get("total", len(tests)),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "errors": summary.get("error", 0),
            "skipped": summary.get("skipped", 0),
            "duration": data.get("duration", 0.0),
            "failure_details": failures,
        }

    def _ai_analysis(self, summary: dict[str, Any]) -> str:
        failure_text = "\n".join(
            f"  [{i + 1}] {f['nodeid']}\n      {f['message'][:200]}"
            for i, f in enumerate(summary["failure_details"])
        ) or "  (none)"

        prompt = _ANALYSIS_PROMPT.format(
            total=summary["total"],
            passed=summary["passed"],
            failed=summary["failed"],
            errors=summary["errors"],
            skipped=summary["skipped"],
            duration=summary["duration"],
            failures=failure_text,
        )
        try:
            response = self._client.chat.completions.create(
                model=self._config.ai_model,
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover
            logger.error("LLM analysis failed: %s", exc)
            return self._rule_based_analysis(summary)

    @staticmethod
    def _rule_based_analysis(summary: dict[str, Any]) -> str:
        lines = [
            "=== Test Run Analysis ===",
            f"Total : {summary['total']}",
            f"Passed: {summary['passed']}",
            f"Failed: {summary['failed']}",
            f"Errors: {summary['errors']}",
            f"Skipped: {summary['skipped']}",
            f"Duration: {summary['duration']:.1f}s",
        ]
        if summary["failure_details"]:
            lines.append("\nFailed tests:")
            for f in summary["failure_details"]:
                lines.append(f"  • {f['nodeid']}")
                if f["message"]:
                    lines.append(f"    {f['message'][:200]}")
        else:
            lines.append("\nAll tests passed ✓")
        return "\n".join(lines)
