# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Build a self-contained native NumPy model host and its real seed weights."""

from __future__ import annotations

import hashlib
from importlib.metadata import distribution
import json
from pathlib import Path
import subprocess
import sys
import sysconfig

SUITE = Path(__file__).resolve().parents[1]
ROOT = SUITE.parents[1]
PRODUCT43 = ROOT / "12-AZ-IP/43-az-geometric-tori-transformer"
sys.path.insert(0, str(PRODUCT43))

from az_tori_transformer import train_text_file
from psicat_core import PROFILE


def main() -> None:
    output = SUITE / "build/native"
    output.mkdir(parents=True, exist_ok=True)
    python_license = next((candidate for candidate in (
        Path(sys.base_prefix) / "LICENSE.txt", Path(sysconfig.get_path("stdlib")) / "LICENSE.txt"
    ) if candidate.is_file()), None)
    if python_license is None:
        raise FileNotFoundError("The CPython redistribution license is missing.")
    notices = [f"CPython {sys.version}\n\n{python_license.read_text(encoding='utf-8')}"]
    for package in ("numpy", "pyinstaller"):
        installed = distribution(package)
        licenses = [file for file in installed.files or [] if file.name.upper().startswith(("LICENSE", "COPYING", "COPYRIGHT"))]
        if not licenses:
            raise FileNotFoundError(f"Redistribution license for {package} is missing.")
        for file in licenses:
            notices.append(f"{package} {installed.version}: {file}\n\n{installed.locate_file(file).read_text(encoding='utf-8')}")
    (output / "NATIVE-LICENSES.txt").write_text("\n\n".join(notices), encoding="utf-8")
    # Only reviewed public repository documentation enters the initial research model.
    sources = [
        "12-AZ-IP/20-psicat-navigator/README.md",
        "12-AZ-IP/43-az-geometric-tori-transformer/README.md",
        "12-AZ-IP/45-axiomzero-pc-suite/README.md",
        "12-AZ-IP/README.md",
    ]
    corpus = output / "seed-corpus.txt"
    corpus.write_text(
        "\n\n".join(f"Source: {name}\n{(ROOT / name).read_text(encoding='utf-8')}" for name in sources),
        encoding="utf-8", newline="",
    )
    report = train_text_file(corpus, output / "psicat-seed.npz", steps=500, **PROFILE)
    receipt = {
        "schema": "psicat-native-seed-v1", "sources": sources, "training": report,
        "sourceSha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources},
        "checkpointSha256": hashlib.sha256((output / "psicat-seed.npz").read_bytes()).hexdigest(),
        "scope": "Own toroidal character-model seed; experimental generation, not a verified production assistant.",
    }
    (output / "seed-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
        "--name", "PsiCatCore", "--paths", str(PRODUCT43), "--collect-all", "numpy",
        "--distpath", str(output), "--workpath", str(SUITE / "build/pyinstaller"),
        "--specpath", str(SUITE / "build"), str(SUITE / "scripts/psicat_core.py"),
    ], check=True)


if __name__ == "__main__":
    main()
