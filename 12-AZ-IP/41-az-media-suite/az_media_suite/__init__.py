# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Media & Feature-Inspection Suite — Product 41.

Gives PsiCat/Merlin four related, stdlib-first abilities requested for the
"collected suite": a comic-archive viewer, audio understanding/creation,
lightweight video (frame-sequence) understanding/creation, and an
evidence-cited, source-only feature inspector for web/Electron-style apps.

Epistemic status: the feature inspector is an original, independent
reimplementation of the *evidence-based feature discovery* idea popularized
by third-party tools such as github.com/morluto/rea. It does not depend on,
bundle, or call that project's npm package or MCP server, and it does not
perform native-binary reverse engineering (no Hopper/Ghidra/IDA
integration). It only reads locally available source text (HTML/JS/TS) and
reports findings with file/line citations — adapted to this repository's
Python-only, source-only, no-foreign-code-execution conventions.
"""

from .comic import (
    ComicPage,
    ComicInspection,
    inspect_comic_archive,
    create_comic_archive,
    read_comic_page,
)
from .audio import (
    AudioInspection,
    inspect_audio_file,
    synthesize_tone,
    create_tone_sequence_wav,
)
from .video import (
    VideoInspection,
    inspect_video_container,
    create_video_container,
)
from .feature_inspection import (
    InspectionFinding,
    FeatureInspectionReport,
    scan_app_features,
)
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "ComicPage",
    "ComicInspection",
    "inspect_comic_archive",
    "create_comic_archive",
    "read_comic_page",
    "AudioInspection",
    "inspect_audio_file",
    "synthesize_tone",
    "create_tone_sequence_wav",
    "VideoInspection",
    "inspect_video_container",
    "create_video_container",
    "InspectionFinding",
    "FeatureInspectionReport",
    "scan_app_features",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.0.0"
