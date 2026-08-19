# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""az_ip_common/logger.py — Structured JSON-line logger factory."""
from __future__ import annotations

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Return a logger configured for structured JSON output.

    Falls back to standard logging if structlog is not installed.
    """
    try:
        import structlog  # type: ignore

        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, (level or "INFO").upper(), logging.INFO)
            ),
            logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        )
        return structlog.get_logger(name)  # type: ignore[return-value]
    except ImportError:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(
                logging.Formatter(
                    '{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}'
                )
            )
            logger.addHandler(handler)
        logger.setLevel(getattr(logging, (level or "INFO").upper(), logging.INFO))
        return logger
