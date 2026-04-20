"""Centralised logging setup."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from framework.utils.config import Config

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str = "unified_test") -> logging.Logger:
    """Return a named logger with consistent formatting.

    Re-uses existing loggers so that configuration is not duplicated.
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    config = Config()
    log_level = getattr(logging, config.log_level, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(_build_formatter())
        logger.addHandler(console_handler)

        # File handler
        log_file = _ensure_log_dir() / "test_run.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(_build_formatter(with_color=False))
        logger.addHandler(file_handler)

    logger.propagate = False
    _LOGGERS[name] = logger
    return logger


def _build_formatter(with_color: bool = True) -> logging.Formatter:
    if with_color:
        fmt = (
            "\033[36m%(asctime)s\033[0m | "
            "%(levelname)-8s | "
            "\033[35m%(name)s\033[0m | "
            "%(message)s"
        )
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    return logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")


def _ensure_log_dir() -> Path:
    config = Config()
    log_dir = config.report_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
