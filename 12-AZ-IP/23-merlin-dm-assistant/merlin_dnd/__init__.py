# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Merlin DM Guide & Player Assistant core package."""

from .assistant import build_merlin_response
from .server import dispatch_request, serve
from .service import MerlinDndService

__all__ = ["MerlinDndService", "build_merlin_response", "dispatch_request", "serve"]
