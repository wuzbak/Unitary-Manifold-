#!/usr/bin/env python3
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
axiomzero_bootstrap.py — AxiomZero Unitary Operating System Bootstrap

THE ONE COMMAND THAT UNCURLS AXIOMZERO FROM COMPACTIFIED SPACE.

Usage (any platform with Python 3.10+):

    python3 axiomzero_bootstrap.py [--mode cognitive|kernel|full]
                                   [--cpu-only]
                                   [--no-service]
                                   [--check]

Modes:
  cognitive  (default) — Install the Python cognitive layer (7-manager network,
                          Ollama, Continue.dev config).  Works on all platforms.
  kernel               — Build the AZ-KERNEL Rust bare-metal binary.
                          Requires Rust toolchain.  Produces az-kernel.efi.
  full                 — Both cognitive and kernel modes.

Options:
  --cpu-only    Use CPU-only Ollama models (for machines without NVIDIA GPU).
  --no-service  Skip registering AxiomZero as a system service.
  --check       Check prerequisites without installing anything.

Platform support:
  Windows 10+   (PowerShell 5+, winget, NSSM for service registration)
  macOS 12+     (Homebrew, launchd for service registration)
  Linux x86-64  (apt/brew/pip, systemd for service registration)
  Android       (Termux, remote mode pointing to Omen 45L)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, installer engineering: GitHub Copilot (AI).
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

# ── Constants ──────────────────────────────────────────────────────────────
VERSION = "0.1.0"
REPO_URL = "https://github.com/wuzbak/Unitary-Manifold-"
MIN_PYTHON = (3, 10)
MIN_RAM_GB = 4
RECOMMENDED_RAM_GB = 16

AZ_HOME = Path.home() / ".axiomzero"
AZ_CONFIG = AZ_HOME / "config.json"
AZ_LOG = AZ_HOME / "bootstrap.log"

REPO_ROOT = Path(__file__).parent

# Ollama models for the cognitive layer
OLLAMA_MODELS = {
    "manager": "llama3.1:8b",      # for M1–M2–M7 strategic reasoning
    "coding": "qwen2.5-coder:7b",  # for M3 symbolic math + M4 test guard
    "embed":  "nomic-embed-text",  # for M5 corpus RAG indexing
}
OLLAMA_MODELS_CPU = {
    "manager": "llama3.2:3b",           # lighter model for CPU-only
    "coding": "qwen2.5-coder:1.5b",
    "embed":  "nomic-embed-text",
}

CONTINUE_CONFIG = {
    "models": [
        {"title": "Qwen 2.5 Coder (7B) — AxiomZero", "provider": "ollama", "model": "qwen2.5-coder:7b"},
        {"title": "Llama 3.1 (8B) — AxiomZero",      "provider": "ollama", "model": "llama3.1:8b"},
    ],
    "tabAutocompleteModel": {
        "title": "Qwen 2.5 Coder", "provider": "ollama", "model": "qwen2.5-coder:7b"
    },
    "embeddingsProvider": {
        "provider": "ollama", "model": "nomic-embed-text"
    },
}


# ── Platform Detection ─────────────────────────────────────────────────────

def detect_platform() -> str:
    """Return 'windows', 'macos', 'linux', or 'android'."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        # Detect Termux (Android)
        if "com.termux" in os.environ.get("PREFIX", "") or Path("/data/data/com.termux").exists():
            return "android"
        return "linux"
    return "linux"  # safe default


def detect_gpu() -> bool:
    """Return True if an NVIDIA GPU with ≥ 6 GB VRAM is detected."""
    nvidia = shutil.which("nvidia-smi")
    if nvidia:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            )
            vram_mb = int(result.stdout.strip().split("\n")[0])
            return vram_mb >= 6 * 1024
        except Exception:
            pass
    return False


def get_ram_gb() -> float:
    """Return total system RAM in GB."""
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        pass
    # Fallback: read /proc/meminfo on Linux
    try:
        mem_info = Path("/proc/meminfo").read_text()
        for line in mem_info.splitlines():
            if line.startswith("MemTotal:"):
                kb = int(line.split()[1])
                return kb / (1024 ** 2)
    except Exception:
        pass
    return 16.0  # assume 16 GB if unknown


# ── Prerequisite Checks ────────────────────────────────────────────────────

def check_python() -> tuple[bool, str]:
    version = sys.version_info[:2]
    if version < MIN_PYTHON:
        return False, f"Python {'.'.join(map(str, MIN_PYTHON))}+ required, found {'.'.join(map(str, version))}"
    return True, f"Python {sys.version.split()[0]} ✅"


def check_rust() -> tuple[bool, str]:
    if shutil.which("cargo"):
        try:
            result = subprocess.run(["cargo", "--version"], capture_output=True, text=True, timeout=5)
            return True, f"{result.stdout.strip()} ✅"
        except Exception:
            pass
    return False, "cargo not found — install from https://rustup.rs/"


def check_ollama() -> tuple[bool, str]:
    if shutil.which("ollama"):
        try:
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
            return True, f"{result.stdout.strip()} ✅"
        except Exception:
            return True, "Ollama installed ✅"
    return False, "Ollama not installed — https://ollama.ai"


def check_all() -> bool:
    """Run all prerequisite checks and print results."""
    print(f"\n{'─'*50}")
    print(f"  AxiomZero Bootstrap — Prerequisite Check")
    print(f"  Platform: {detect_platform()}  |  GPU: {'✅' if detect_gpu() else '❌ (CPU mode)'}")
    print(f"  RAM: {get_ram_gb():.1f} GB")
    print(f"{'─'*50}")

    all_ok = True
    checks = [
        ("Python", check_python),
        ("Rust/cargo", check_rust),
        ("Ollama", check_ollama),
    ]
    for name, fn in checks:
        ok, msg = fn()
        icon = "✅" if ok else "⚠️ "
        print(f"  {icon} {name}: {msg}")
        if not ok:
            all_ok = False
    print()
    return all_ok


# ── Installation Steps ─────────────────────────────────────────────────────

def install_ollama(platform_id: str) -> bool:
    """Install Ollama if not present."""
    ok, _ = check_ollama()
    if ok:
        print("[bootstrap] Ollama already installed.")
        return True

    print("[bootstrap] Installing Ollama...")
    if platform_id == "linux":
        try:
            subprocess.run(
                "curl -fsSL https://ollama.ai/install.sh | sh",
                shell=True, check=True, timeout=120,
            )
            return True
        except Exception as exc:
            print(f"[bootstrap] Ollama install failed: {exc}")
            print("[bootstrap] Manual install: https://ollama.ai/download")
            return False
    elif platform_id == "macos":
        print("[bootstrap] macOS: Please download Ollama from https://ollama.ai/download/mac")
        print("            Then run: brew install ollama  OR  use the .dmg installer")
        return False
    elif platform_id == "windows":
        print("[bootstrap] Windows: Please download Ollama from https://ollama.ai/download/windows")
        return False
    elif platform_id == "android":
        print("[bootstrap] Android: Ollama is not supported natively.")
        print("            Set AXIOMZERO_OLLAMA_HOST=http://<your-omen-ip>:11434")
        return True  # remote mode
    return False


def pull_ollama_models(cpu_only: bool) -> None:
    """Pull required Ollama models."""
    models = OLLAMA_MODELS_CPU if cpu_only else OLLAMA_MODELS
    for role, model in models.items():
        print(f"[bootstrap] Pulling Ollama model [{role}]: {model} ...")
        try:
            subprocess.run(["ollama", "pull", model], check=True, timeout=600)
            print(f"[bootstrap] ✅ {model} ready.")
        except subprocess.CalledProcessError as exc:
            print(f"[bootstrap] ⚠️  Failed to pull {model}: {exc}")
        except FileNotFoundError:
            print(f"[bootstrap] ⚠️  ollama not in PATH — skipping model pull.")
            break


def write_continue_config(cpu_only: bool) -> None:
    """Write Continue.dev config.json."""
    config = CONTINUE_CONFIG.copy()
    if cpu_only:
        for m in config["models"]:
            m["model"] = m["model"].replace("7b", "1.5b").replace("8b", "3b")
        config["tabAutocompleteModel"]["model"] = "qwen2.5-coder:1.5b"

    # VS Code / JetBrains Continue config location
    continue_dirs = [
        Path.home() / ".continue",
        Path.home() / "Library" / "Application Support" / "Continue",
        Path(os.environ.get("APPDATA", "")) / "Continue" if os.name == "nt" else Path("/nonexistent"),
    ]
    for d in continue_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
            config_file = d / "config.json"
            config_file.write_text(json.dumps(config, indent=2))
            print(f"[bootstrap] ✅ Continue.dev config written: {config_file}")
            break
        except Exception:
            continue


def write_axiomzero_config(platform_id: str, cpu_only: bool, has_gpu: bool) -> None:
    """Write ~/.axiomzero/config.json."""
    AZ_HOME.mkdir(parents=True, exist_ok=True)
    config = {
        "version": VERSION,
        "platform": platform_id,
        "repo_root": str(REPO_ROOT),
        "cpu_only": cpu_only,
        "has_gpu": has_gpu,
        "ollama_host": os.environ.get("AXIOMZERO_OLLAMA_HOST", "http://localhost:11434"),
        "models": OLLAMA_MODELS_CPU if cpu_only else OLLAMA_MODELS,
        "db_path": str(AZ_HOME / "state.db"),
        "log_path": str(AZ_LOG),
        "winding_number": 5,
        "k_cs": 74,
        "n_s_predicted": 0.9635,
        "r_braided": 0.0315,
    }
    AZ_CONFIG.write_text(json.dumps(config, indent=2))
    print(f"[bootstrap] ✅ AxiomZero config written: {AZ_CONFIG}")


def register_service(platform_id: str) -> bool:
    """Register AxiomZero as a system service."""
    daemon_script = REPO_ROOT / "az-os" / "daemon.py"
    if not daemon_script.exists():
        # Create a minimal daemon entry point
        daemon_script.write_text(textwrap.dedent(f"""\
            #!/usr/bin/env python3
            # AxiomZero cognitive layer daemon entry point
            import sys
            sys.path.insert(0, "{REPO_ROOT}")
            from az_os.agent_core import AgentCore
            core = AgentCore(interactive=False)
            core.boot()
            # Block forever — the monitoring thread runs in background.
            import time
            while True:
                time.sleep(3600)
        """))

    if platform_id == "linux":
        service_content = textwrap.dedent(f"""\
            [Unit]
            Description=AxiomZero Cognitive Layer Daemon
            After=network.target

            [Service]
            Type=simple
            User={os.getlogin()}
            ExecStart={sys.executable} {daemon_script}
            Restart=on-failure
            RestartSec=30
            Environment=PYTHONPATH={REPO_ROOT}

            [Install]
            WantedBy=multi-user.target
        """)
        service_path = Path.home() / ".config" / "systemd" / "user" / "axiomzero.service"
        service_path.parent.mkdir(parents=True, exist_ok=True)
        service_path.write_text(service_content)
        print(f"[bootstrap] ✅ systemd user service written: {service_path}")
        print(f"[bootstrap]    Enable: systemctl --user enable axiomzero")
        print(f"[bootstrap]    Start:  systemctl --user start axiomzero")
        return True

    elif platform_id == "macos":
        plist_content = textwrap.dedent(f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
              "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
              <key>Label</key><string>org.axiomzero.daemon</string>
              <key>ProgramArguments</key>
              <array>
                <string>{sys.executable}</string>
                <string>{daemon_script}</string>
              </array>
              <key>RunAtLoad</key><true/>
              <key>KeepAlive</key><true/>
              <key>EnvironmentVariables</key>
              <dict>
                <key>PYTHONPATH</key><string>{REPO_ROOT}</string>
              </dict>
            </dict>
            </plist>
        """)
        plist_path = Path.home() / "Library" / "LaunchAgents" / "org.axiomzero.daemon.plist"
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        plist_path.write_text(plist_content)
        print(f"[bootstrap] ✅ launchd plist written: {plist_path}")
        print(f"[bootstrap]    Load: launchctl load {plist_path}")
        return True

    elif platform_id == "windows":
        bat_path = AZ_HOME / "start_axiomzero.bat"
        bat_path.write_text(
            f'@echo off\r\n"{sys.executable}" "{daemon_script}"\r\n'
        )
        print(f"[bootstrap] ✅ Windows startup script: {bat_path}")
        print("[bootstrap]    For autostart: Add to Task Scheduler or NSSM")
        print(f"            NSSM: nssm install AxiomZero \"{sys.executable}\" \"{daemon_script}\"")
        return True

    return False


# ── Kernel Build ────────────────────────────────────────────────────────────

def build_kernel() -> bool:
    """Build the AZ-KERNEL Rust binary."""
    ok, msg = check_rust()
    if not ok:
        print(f"[bootstrap] ⚠️  Rust not available: {msg}")
        print("[bootstrap]    Install Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
        return False

    kernel_dir = REPO_ROOT / "az-kernel"
    if not kernel_dir.exists():
        print("[bootstrap] ⚠️  az-kernel/ directory not found.")
        return False

    build_script = kernel_dir / "scripts" / "build.sh"
    if not build_script.exists():
        print("[bootstrap] ⚠️  az-kernel/scripts/build.sh not found.")
        return False

    print("[bootstrap] Building AZ-KERNEL (Rust bare-metal binary)...")
    try:
        subprocess.run(["bash", str(build_script)], cwd=str(kernel_dir), check=True, timeout=300)
        print("[bootstrap] ✅ AZ-KERNEL build complete.")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[bootstrap] ⚠️  Kernel build failed: {exc}")
        return False


# ── Main Entry Point ────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AxiomZero Bootstrap — uncurl the OS from compactified space.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode", choices=["cognitive", "kernel", "full"], default="cognitive",
        help="Installation mode (default: cognitive)",
    )
    parser.add_argument("--cpu-only", action="store_true",
                        help="Use CPU-only Ollama models (no GPU required)")
    parser.add_argument("--no-service", action="store_true",
                        help="Skip system service registration")
    parser.add_argument("--check", action="store_true",
                        help="Check prerequisites only, do not install")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        AxiomZero Unitary Operating System — Bootstrap        ║
║        v{VERSION}                                               ║
║                                                              ║
║  Theory:  ThomasCory Walker-Pearson                          ║
║  Kernel:  GitHub Copilot (AI)                                ║
║  Repo:    {REPO_URL}  ║
╚══════════════════════════════════════════════════════════════╝
""")

    platform_id = detect_platform()
    has_gpu = detect_gpu()
    cpu_only = args.cpu_only or not has_gpu

    if args.check or True:  # always run checks first
        ok = check_all()
        if args.check:
            sys.exit(0 if ok else 1)

    if args.mode in ("cognitive", "full"):
        print("\n[bootstrap] === COGNITIVE LAYER INSTALLATION ===\n")
        install_ollama(platform_id)
        pull_ollama_models(cpu_only)
        write_continue_config(cpu_only)
        write_axiomzero_config(platform_id, cpu_only, has_gpu)
        if not args.no_service:
            register_service(platform_id)

    if args.mode in ("kernel", "full"):
        print("\n[bootstrap] === KERNEL BUILD ===\n")
        build_kernel()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  AxiomZero Bootstrap Complete                                ║
║                                                              ║
║  Config:    {str(AZ_CONFIG):<48} ║
║                                                              ║
║  To start the cognitive layer:                               ║
║    python3 -c "                                              ║
║      import sys; sys.path.insert(0, '{REPO_ROOT}')       ║
║      from az_os.agent_core import AgentCore                  ║
║      AgentCore().boot()"                                     ║
║                                                              ║
║  To run the test suite:                                      ║
║    python3 -m pytest tests/ recycling/ -q                    ║
║                                                              ║
║  To build the bare-metal kernel:                             ║
║    cd az-kernel && bash scripts/build.sh                     ║
║    bash scripts/qemu_run.sh                                  ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
