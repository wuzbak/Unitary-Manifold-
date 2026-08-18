# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""az_ip_common/config.py — Pydantic-settings config loader."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings  # type: ignore
    from pydantic import Field
except ImportError:
    from dataclasses import dataclass as _dc  # type: ignore
    class BaseSettings:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    def Field(default=None, **kwargs):  # type: ignore
        return default


class AZIPConfig(BaseSettings):
    """Configuration for AZ-IP apps loaded from environment variables."""

    # AxiomZero API
    axiomzero_url: str = Field(default="http://localhost:8000", validation_alias="AXIOMZERO_URL")
    axiomzero_jwt: str = Field(default="", validation_alias="AXIOMZERO_JWT")

    # UM-SOS API
    umos_url: str = Field(default="http://localhost:8001", validation_alias="UMOS_URL")

    # Logging
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field(default="json", validation_alias="LOG_FORMAT")

    # Storage
    data_dir: Path = Field(default=Path.home() / ".az-ip", validation_alias="AZIP_DATA_DIR")

    # Observability
    otlp_endpoint: Optional[str] = Field(default=None, validation_alias="OTLP_ENDPOINT")
    prometheus_port: Optional[int] = Field(default=None, validation_alias="PROMETHEUS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
