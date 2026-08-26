# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Constants for the standalone OX Navigator product."""

WINDING_NUMBER = 5
K_CS = 74
N_S = 0.9635
R_BRAIDED = 0.0315
BETA_C1 = 0.273
BETA_C2 = 0.331
MODEL_ID = "stealth/ox-alpha"
API_BASE = "https://openrouter.ai/api/v1"
MAX_HISTORY = 12
DEFAULT_TEMPERATURE = 0.3
GATE_LABELS = [
    "HARDGATE",
    "ADJACENT_TRACK",
    "OPEN_GAP",
    "ARCHITECTURE_LIMIT",
    "GOVERNANCE",
]
EXAMPLE_QUERIES = [
    "Which pillar closes the Δm²₂₁ tension?",
    "List all OPEN_GAP claims and their current σ tensions.",
    "What Lean4 theorems cover winding number selection n_w=5?",
    "Summarise the birefringence falsification conditions for LiteBIRD.",
    "Which pillars address the CMB amplitude suppression (Admission 1)?",
    "What is the difference between a hardgate pillar and an adjacent track?",
    "Which tests cover the holographic entropy-area relation (Pillar 4)?",
    "Explain the HILS governance boundary (SEPARATION.md).",
]
