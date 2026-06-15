# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero Bootstrap — Phase 0: "The Uncompactification Event"

Single entry-point installer.  One command, one file, any device.

Usage::

    python axiomzero_bootstrap.py [--mode={full,thin-client,cpu-only}]
                                  [--server=http://HOST:8000]
                                  [--repo-root=/path/to/Unitary-Manifold]
                                  [--skip-ollama] [--skip-vectordb]
                                  [--skip-service] [--skip-tests]

The bootstrap is idempotent: running it multiple times produces the same
final state (topological invariant).

Platforms: Windows, macOS, Linux, Android/Termux

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MIN_PYTHON = (3, 10)
AZ_DIR = Path.home() / ".axiomzero"
CONFIG_FILE = AZ_DIR / "config.json"
STATE_DB = AZ_DIR / "state.db"

OLLAMA_MODELS_FULL = ["llama3.1:8b", "qwen2.5-coder:7b", "nomic-embed-text"]
OLLAMA_MODELS_CPU = ["qwen2.5-coder:1.5b", "nomic-embed-text"]

CHROMA_PORT = 8001
OLLAMA_PORT = 11434
AXIOMZERO_PORT = 8000

REPO_ROOT_DEFAULT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _log(msg: str, level: str = "INFO") -> None:
    prefix = {"INFO": "✦", "WARN": "⚠", "ERROR": "✗", "OK": "✔"}.get(level, "·")
    print(f"  {prefix}  {msg}", flush=True)


def _run(cmd: list[str], check: bool = True, capture: bool = False, **kw) -> subprocess.CompletedProcess:
    """Run a subprocess command with logging."""
    _log(f"$ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(
        cmd, check=check, capture_output=capture,
        text=True, **kw
    )


def _detect_platform() -> str:
    """Return a canonical platform string."""
    sys_name = platform.system().lower()
    if sys_name == "linux":
        # Check for Termux (Android)
        if "com.termux" in os.environ.get("PREFIX", "") or Path("/data/data/com.termux").exists():
            return "android"
        return "linux"
    if sys_name == "darwin":
        return "macos"
    if sys_name == "windows":
        return "windows"
    return "unknown"


def _is_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Phase 0.1 — Python version check
# ---------------------------------------------------------------------------

def check_python_version() -> None:
    print("\n── Phase 0.1: Python version ──")
    v = sys.version_info[:2]
    if v < MIN_PYTHON:
        _log(f"Python {v[0]}.{v[1]} detected. AxiomZero requires Python "
             f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+. Aborting.", "ERROR")
        sys.exit(1)
    _log(f"Python {v[0]}.{v[1]} — OK", "OK")


# ---------------------------------------------------------------------------
# Phase 0.2 — Install Python dependencies
# ---------------------------------------------------------------------------

def install_python_deps(cpu_only: bool = False) -> None:
    print("\n── Phase 0.2: Python dependencies ──")
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        _run([sys.executable, "-m", "pip", "install", "-q", "-r", str(req_file)])
    else:
        # Inline minimal set
        core_pkgs = [
            "fastapi>=0.110", "uvicorn[standard]>=0.29",
            "httpx>=0.27", "aiofiles>=23.2",
            "chromadb>=0.4", "sentence-transformers>=2.7",
            "langgraph>=0.1", "langchain-community>=0.2",
        ]
        if not cpu_only:
            core_pkgs.append("playwright>=1.44")
        _run([sys.executable, "-m", "pip", "install", "-q"] + core_pkgs)
    _log("Python dependencies installed", "OK")


# ---------------------------------------------------------------------------
# Phase 0.3 — Ollama
# ---------------------------------------------------------------------------

def install_ollama(plat: str, models: list[str], skip: bool = False) -> Optional[str]:
    print("\n── Phase 0.3: Ollama ──")
    if skip:
        _log("Skipping Ollama install (--skip-ollama)", "WARN")
        return None

    if _is_command("ollama"):
        _log("Ollama already installed", "OK")
    else:
        _log("Installing Ollama…")
        if plat in ("linux", "macos"):
            _run(["bash", "-c", "curl -fsSL https://ollama.com/install.sh | sh"])
        elif plat == "android":
            _log("Android: Ollama remote mode — point to desktop server", "WARN")
            return None
        elif plat == "windows":
            _log("Windows: download Ollama installer from https://ollama.com/download", "WARN")
            _log("After manual install, re-run bootstrap.", "WARN")
            return None
        else:
            _log("Unknown platform — manual Ollama install required", "WARN")
            return None

    # Pull models
    for model in models:
        _log(f"Pulling {model}…")
        result = _run(["ollama", "pull", model], check=False)
        if result.returncode == 0:
            _log(f"  {model} ready", "OK")
        else:
            _log(f"  {model} pull failed (network issue?)", "WARN")

    return f"http://localhost:{OLLAMA_PORT}"


# ---------------------------------------------------------------------------
# Phase 0.4 — Vector database (ChromaDB)
# ---------------------------------------------------------------------------

def start_vectordb(skip: bool = False) -> Optional[str]:
    print("\n── Phase 0.4: Vector database (ChromaDB) ──")
    if skip:
        _log("Skipping vector DB (--skip-vectordb)", "WARN")
        return None

    # Try Docker first
    if _is_command("docker"):
        result = _run(
            ["docker", "ps", "--filter", f"name=axiomzero-chroma",
             "--format", "{{.Names}}"],
            capture=True, check=False,
        )
        if "axiomzero-chroma" in (result.stdout or ""):
            _log("ChromaDB container already running", "OK")
        else:
            _log("Starting ChromaDB via Docker…")
            _run([
                "docker", "run", "-d",
                "--name", "axiomzero-chroma",
                "--restart", "unless-stopped",
                "-p", f"{CHROMA_PORT}:{CHROMA_PORT}",
                "-v", str(AZ_DIR / "chroma_data") + ":/chroma/chroma",
                "chromadb/chroma:latest",
            ], check=False)
        return f"http://localhost:{CHROMA_PORT}"
    else:
        # Native ChromaDB (already installed as Python package)
        _log("Docker not found — will use in-process ChromaDB", "WARN")
        _ensure_dir(AZ_DIR / "chroma_data")
        return f"local:{AZ_DIR / 'chroma_data'}"


# ---------------------------------------------------------------------------
# Phase 0.5 — RAG indexing
# ---------------------------------------------------------------------------

def run_rag_index(repo_root: Path, vectordb_url: Optional[str]) -> None:
    print("\n── Phase 0.5: RAG indexing ──")
    rag_script = repo_root / "bot" / "rag_index.py"
    az_rag_script = repo_root / "AxiomZero" / "memory" / "vector_store.py"

    if rag_script.exists():
        _log(f"Running existing RAG indexer: {rag_script}")
        env = os.environ.copy()
        if vectordb_url:
            env["AXIOMZERO_VECTORDB_URL"] = vectordb_url
        env["AXIOMZERO_REPO_ROOT"] = str(repo_root)
        result = _run([sys.executable, str(rag_script)], check=False, env=env)
        if result.returncode != 0:
            _log("RAG indexing returned non-zero (may be OK if deps missing)", "WARN")
        else:
            _log("RAG indexing complete", "OK")
    else:
        _log("bot/rag_index.py not found — skipping", "WARN")


# ---------------------------------------------------------------------------
# Phase 0.6 — Service registration
# ---------------------------------------------------------------------------

def register_service(plat: str, repo_root: Path, skip: bool = False) -> None:
    print("\n── Phase 0.6: Service registration ──")
    if skip:
        _log("Skipping service registration (--skip-service)", "WARN")
        return

    az_api = repo_root / "AxiomZero" / "api" / "server.py"
    start_cmd = f"{sys.executable} -m uvicorn axiomzero.api.server:app --host 0.0.0.0 --port {AXIOMZERO_PORT}"

    if plat == "linux":
        _register_systemd(start_cmd, repo_root)
    elif plat == "macos":
        _register_launchd(start_cmd, repo_root)
    elif plat == "windows":
        _register_task_scheduler(start_cmd, repo_root)
    elif plat == "android":
        _register_termux(start_cmd, repo_root)
    else:
        _log(f"Unknown platform '{plat}' — service registration skipped", "WARN")


def _register_systemd(start_cmd: str, repo_root: Path) -> None:
    unit = textwrap.dedent(f"""\
        [Unit]
        Description=AxiomZero AI Cognitive Layer
        After=network.target

        [Service]
        Type=simple
        User={os.getenv('USER', 'user')}
        WorkingDirectory={repo_root}
        ExecStart={start_cmd}
        Restart=on-failure
        RestartSec=10
        Environment=PYTHONPATH={repo_root}

        [Install]
        WantedBy=multi-user.target
    """)
    unit_path = Path("/etc/systemd/system/axiomzero.service")
    try:
        unit_path.write_text(unit)
        _run(["systemctl", "daemon-reload"], check=False)
        _run(["systemctl", "enable", "--now", "axiomzero"], check=False)
        _log("systemd unit registered and started", "OK")
    except PermissionError:
        # User-level fallback
        user_unit_dir = Path.home() / ".config" / "systemd" / "user"
        user_unit_dir.mkdir(parents=True, exist_ok=True)
        (user_unit_dir / "axiomzero.service").write_text(unit)
        _run(["systemctl", "--user", "daemon-reload"], check=False)
        _run(["systemctl", "--user", "enable", "--now", "axiomzero"], check=False)
        _log("systemd user unit registered", "OK")


def _register_launchd(start_cmd: str, repo_root: Path) -> None:
    plist = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
          "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.axiomzero.daemon</string>
            <key>ProgramArguments</key>
            <array>
                {"".join(f"<string>{p}</string>" for p in start_cmd.split())}
            </array>
            <key>WorkingDirectory</key>
            <string>{repo_root}</string>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <true/>
            <key>StandardOutPath</key>
            <string>{AZ_DIR}/axiomzero.log</string>
            <key>StandardErrorPath</key>
            <string>{AZ_DIR}/axiomzero.err</string>
        </dict>
        </plist>
    """)
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_path = plist_dir / "com.axiomzero.daemon.plist"
    plist_path.write_text(plist)
    _run(["launchctl", "load", "-w", str(plist_path)], check=False)
    _log("launchd plist registered", "OK")


def _register_task_scheduler(start_cmd: str, repo_root: Path) -> None:
    _log("Windows: creating Task Scheduler entry via schtasks")
    parts = start_cmd.split()
    exe = parts[0]
    args = " ".join(parts[1:])
    _run([
        "schtasks", "/Create", "/F",
        "/TN", "AxiomZero",
        "/TR", f'"{exe}" {args}',
        "/SC", "ONLOGON",
        "/RU", os.environ.get("USERNAME", "SYSTEM"),
    ], check=False)
    _log("Task Scheduler entry created", "OK")


def _register_termux(start_cmd: str, repo_root: Path) -> None:
    bashrc = Path.home() / ".bashrc"
    marker = "# AxiomZero autostart"
    autostart_line = f"\n{marker}\n{start_cmd} &\n"
    existing = bashrc.read_text() if bashrc.exists() else ""
    if marker not in existing:
        with open(bashrc, "a") as f:
            f.write(autostart_line)
        _log("Termux ~/.bashrc autostart registered", "OK")
    else:
        _log("Termux autostart already registered", "OK")


# ---------------------------------------------------------------------------
# Phase 0.7 — Validation (subset test run)
# ---------------------------------------------------------------------------

def validate_bootstrap(repo_root: Path, skip: bool = False) -> bool:
    print("\n── Phase 0.7: Bootstrap validation ──")
    if skip:
        _log("Skipping test validation (--skip-tests)", "WARN")
        return True

    az_tests = repo_root / "AxiomZero" / "tests" / "test_axiomzero.py"
    if az_tests.exists():
        _log("Running AxiomZero self-test suite…")
        result = _run(
            [sys.executable, "-m", "pytest", str(az_tests), "-q", "--tb=short"],
            check=False,
        )
        if result.returncode == 0:
            _log("All AxiomZero tests passed — bootstrap validated", "OK")
            return True
        else:
            _log("AxiomZero tests FAILED — check output above", "ERROR")
            return False
    else:
        _log("AxiomZero test file not found — running smoke test")
        # Minimal smoke: import the core
        result = _run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, '.'); "
             "from AxiomZero.core.agent_core import AxiomZeroOrchestrator; "
             "print('Import OK')"],
            check=False,
        )
        ok = result.returncode == 0
        _log("Smoke test " + ("passed" if ok else "FAILED"), "OK" if ok else "ERROR")
        return ok


# ---------------------------------------------------------------------------
# Phase 0.8 — Write config
# ---------------------------------------------------------------------------

def write_config(
    plat: str,
    repo_root: Path,
    ollama_url: Optional[str],
    vectordb_url: Optional[str],
    mode: str,
    thin_server: Optional[str],
) -> dict:
    print("\n── Phase 0.8: Writing config ──")
    _ensure_dir(AZ_DIR)
    config = {
        "version": "1.0",
        "platform": plat,
        "mode": mode,
        "repo_root": str(repo_root),
        "axiomzero_dir": str(AZ_DIR),
        "state_db": str(STATE_DB),
        "ollama_url": ollama_url or f"http://localhost:{OLLAMA_PORT}",
        "vectordb_url": vectordb_url or f"local:{AZ_DIR / 'chroma_data'}",
        "api_port": AXIOMZERO_PORT,
        "thin_client_server": thin_server,
        "models": {
            "strategic": "llama3.1:8b",
            "math": "qwen2.5-coder:7b",
            "test": "qwen2.5-coder:1.5b",
            "embed": "nomic-embed-text",
            "max_concurrent_heavy": 2,
        },
        "hils": {
            "human": "ThomasCory Walker-Pearson",
            "protected_files": ["FALLIBILITY.md", "SEPARATION.md"],
            "protected_actions": [
                "pillar_renumber",
                "authorship_change",
                "falsification_edit",
            ],
        },
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    _log(f"Config written to {CONFIG_FILE}", "OK")
    return config


# ---------------------------------------------------------------------------
# Write Continue.dev IDE config
# ---------------------------------------------------------------------------

def write_continue_config(ollama_url: Optional[str]) -> None:
    print("\n── Continue.dev IDE config ──")
    url = ollama_url or f"http://localhost:{OLLAMA_PORT}"
    config = {
        "models": [
            {
                "title": "AxiomZero — llama3.1:8b",
                "provider": "ollama",
                "model": "llama3.1:8b",
                "apiBase": url,
            },
            {
                "title": "AxiomZero — qwen2.5-coder:7b",
                "provider": "ollama",
                "model": "qwen2.5-coder:7b",
                "apiBase": url,
            },
        ],
        "embeddingsProvider": {
            "provider": "ollama",
            "model": "nomic-embed-text",
            "apiBase": url,
        },
        "contextProviders": [
            {"name": "codebase", "params": {"nRetrieve": 25, "nFinal": 5}},
            {"name": "docs"},
        ],
        "slashCommands": [
            {"name": "edit", "description": "Edit code in place"},
            {"name": "axiomzero", "description": "Route to AxiomZero agent network"},
        ],
    }
    cfg_path = AZ_DIR / "continue_config.json"
    cfg_path.write_text(json.dumps(config, indent=2))
    _log(f"Continue.dev config → {cfg_path}", "OK")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AxiomZero Bootstrap — the Uncompactification Event",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode", choices=["full", "thin-client", "cpu-only"], default="full",
        help="Deployment mode",
    )
    parser.add_argument(
        "--server", default=None,
        help="Remote AxiomZero server URL (thin-client mode)",
    )
    parser.add_argument(
        "--repo-root", default=None,
        help="Path to Unitary Manifold repository root",
    )
    parser.add_argument("--skip-ollama", action="store_true")
    parser.add_argument("--skip-vectordb", action="store_true")
    parser.add_argument("--skip-service", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print("  AxiomZero — The Uncompactification Event")
    print("  Phase 0 Bootstrap")
    print("=" * 60)

    # Determine repo root
    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT_DEFAULT
    if not repo_root.exists():
        _log(f"Repo root not found: {repo_root}", "ERROR")
        sys.exit(1)
    _log(f"Repository root: {repo_root}")

    plat = _detect_platform()
    _log(f"Platform: {plat}")
    _log(f"Mode: {args.mode}")

    # Python check first
    check_python_version()

    # Thin-client mode: skip local services, just configure client
    if args.mode == "thin-client":
        print("\n── Thin-client mode ──")
        if not args.server:
            _log("--server is required in thin-client mode", "ERROR")
            sys.exit(1)
        _run([sys.executable, "-m", "pip", "install", "-q", "httpx>=0.27", "rich>=13"])
        write_config(
            plat, repo_root,
            ollama_url=args.server,
            vectordb_url=None,
            mode="thin-client",
            thin_server=args.server,
        )
        print("\n✔  Thin-client configured. Run:")
        print(f"   python {repo_root / 'AxiomZero' / 'android' / 'client.py'}")
        return

    # CPU-only mode uses smaller models
    models = OLLAMA_MODELS_CPU if args.mode == "cpu-only" else OLLAMA_MODELS_FULL

    # Install Python deps
    install_python_deps(cpu_only=(args.mode == "cpu-only"))

    # Ollama
    ollama_url = install_ollama(plat, models, skip=args.skip_ollama)

    # Vector DB
    vectordb_url = start_vectordb(skip=args.skip_vectordb)

    # RAG index
    run_rag_index(repo_root, vectordb_url)

    # Service registration
    register_service(plat, repo_root, skip=args.skip_service)

    # Write configs
    config = write_config(
        plat, repo_root, ollama_url, vectordb_url,
        mode=args.mode, thin_server=None,
    )
    write_continue_config(ollama_url)

    # Validate
    ok = validate_bootstrap(repo_root, skip=args.skip_tests)

    print("\n" + "=" * 60)
    if ok:
        print("  ✔  AxiomZero bootstrap complete.")
        print(f"     API:    http://localhost:{AXIOMZERO_PORT}")
        print(f"     Config: {CONFIG_FILE}")
        print(f"     Start:  cd {repo_root} && python -m uvicorn AxiomZero.api.server:app --reload")
    else:
        print("  ⚠  Bootstrap completed with warnings.")
        print("     Review output above and re-run failed steps.")
    print("=" * 60)


if __name__ == "__main__":
    main()
