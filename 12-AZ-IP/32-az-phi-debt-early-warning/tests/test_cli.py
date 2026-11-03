# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import json
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from run import main


def test_monitor_cli_requires_and_uses_explicit_observations(capsys):
    result = main([
        "monitor",
        "--capacity", "10",
        "--discharge-rate", "0.5",
        "--steps", "2:1,1:1",
    ])
    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["report"]["capacity"] == 10.0
    assert [reading["debt"] for reading in payload["history"]] == [0.0, 1.5, 2.0]


def test_cli_without_command_does_not_run_sample_data():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_monitor_cli_rejects_nonfinite_inputs(capsys):
    with pytest.raises(SystemExit) as exc:
        main([
            "monitor",
            "--capacity", "nan",
            "--discharge-rate", "0",
            "--steps", "1:1",
        ])
    assert exc.value.code == 2
    assert "capacity must be a finite number" in capsys.readouterr().err
