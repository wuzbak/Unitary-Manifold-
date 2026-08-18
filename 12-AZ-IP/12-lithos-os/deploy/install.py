#!/usr/bin/env python3
"""
LithosOS — Self-Deploy Installer
"""
from __future__ import annotations
import argparse
import os
import platform
import subprocess
import sys
import textwrap
from pathlib import Path

DEPLOY_DIR = Path(__file__).parent
LITHIC_DIR = DEPLOY_DIR.parent
REPO_ROOT = LITHIC_DIR.parent
DATA_DIR = LITHIC_DIR / "data"
VENV_DIR = LITHIC_DIR / ".venv"
LAUNCH_SCRIPT_PY = LITHIC_DIR / "launch.py"
LAUNCH_SCRIPT_SH = LITHIC_DIR / "launch.sh"
LAUNCH_SCRIPT_BAT = LITHIC_DIR / "launch.bat"

CORE_REQUIREMENTS = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.0.0",
    "python-multipart>=0.0.9",
    "gradio>=4.20.0",
    "python-dotenv>=1.0.0",
    "numpy>=1.24",
    "scipy>=1.11",
    "openai>=1.14.0",
    "Pillow>=10.0.0",
]

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

if not sys.stdout.isatty() or platform.system() == "Windows":
    GREEN = YELLOW = RED = CYAN = BOLD = RESET = ""

def _print(msg, colour="", icon=""):
    prefix = f"{colour}{icon}{RESET} " if icon else f"{colour}"
    print(f"{prefix}{msg}{RESET}")

def info(msg): _print(msg, CYAN, "i")
def ok(msg):   _print(msg, GREEN, "+")
def warn(msg): _print(msg, YELLOW, "!")
def err(msg):  _print(msg, RED, "x")

def _detect_platform() -> str:
    if _is_android():
        return "android"
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    if s == "windows":
        return "windows"
    if s == "linux":
        return "linux"
    return "unknown"

def _is_android() -> bool:
    return (
        os.path.exists("/data/data/com.termux") or
        os.getenv("LITHOS_PLATFORM", "") == "android"
    )

def check_python() -> bool:
    return sys.version_info >= (3, 9)

def _check_python_version() -> tuple[bool, str]:
    ok_flag = sys.version_info >= (3, 9)
    ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return ok_flag, ver

def _create_data_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def _create_launch_scripts(app_dir: Path) -> dict:
    sh_path = app_dir / "launch.sh"
    bat_path = app_dir / "launch.bat"
    py_path = app_dir / "launch.py"

    sh_content = textwrap.dedent("""
        #!/bin/bash
        set -e
        cd "$(dirname "$0")"
        python -m lithic.app.main "$@"
    """).strip()
    sh_path.write_text(sh_content)
    try:
        sh_path.chmod(0o755)
    except Exception:
        pass

    bat_content = textwrap.dedent("""
        @echo off
        cd /d "%~dp0"
        python -m lithic.app.main %*
    """).strip()
    bat_path.write_text(bat_content)

    py_content = textwrap.dedent("""
        #!/usr/bin/env python3
        import subprocess, sys
        from pathlib import Path
        subprocess.run([sys.executable, "-m", "lithic.app.main"] + sys.argv[1:])
    """).strip()
    py_path.write_text(py_content)

    return {"sh": sh_path, "bat": bat_path, "py": py_path}

def _install_deps(requirements: list[str]) -> bool:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="LithosOS Installer")
    parser.add_argument("--no-launch", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--android", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--upgrade", action="store_true")
    args = parser.parse_args()

    info("LithosOS Installer")
    platform_name = _detect_platform()
    info(f"Platform: {platform_name}")

    ok_flag, ver = _check_python_version()
    if not ok_flag:
        err(f"Python 3.9+ required, got {ver}")
        sys.exit(1)
    ok(f"Python {ver}")

    if args.check:
        return

    _create_data_dir(DATA_DIR)
    ok(f"Data dir: {DATA_DIR}")

    _create_launch_scripts(LITHIC_DIR)
    ok("Launch scripts created")

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from lithic.app.db.schema import init_db
        from lithic.app.db.seed import seed_database
        init_db(DATA_DIR / "lithos.db")
        seed_database(DATA_DIR / "lithos.db", verbose=False)
        ok("Database initialised")
    except Exception as e:
        warn(f"DB init: {e}")

    if not args.no_launch:
        info("Starting LithosOS...")
        subprocess.Popen([sys.executable, "-m", "lithic.app.main"])

if __name__ == "__main__":
    main()
