# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Directory-hygiene shard for pillars 879-918 (large-directory sharding).

Sharded out of src/core/ to keep the directory's tracked-entry count under
the configured safety limit (TOOLS/checks/large_directory_limits.json).
Modules here are otherwise ordinary src/core pillar modules; import by full
dotted path, e.g. ``from src.core.pillar_0879_0918.pillar879_desi_dr3_routing_update
import ...``.
"""
