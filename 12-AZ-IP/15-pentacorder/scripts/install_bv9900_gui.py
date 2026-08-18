#!/usr/bin/env python3
"""
install_bv9900_gui.py — Tkinter GUI installer for BV9900 Pro
============================================================
Wraps install_bv9900.sh in a user-friendly window with:
  - Live ADB device status
  - Progress bar
  - Per-step status indicators (✓ / ✗ / …)
  - "Fix Child Lock", "Install Termux", "Install GibberNode", "Configure Boot" buttons
  - APK file picker

Requirements: Python 3.8+  (tkinter is in the stdlib; adb must be in PATH)
Usage:
  python3 install_bv9900_gui.py [--apk path/to/GibberNode.apk]
"""

import os
import sys
import subprocess
import threading
import queue
import argparse
import time
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    sys.exit("tkinter not found. Install python3-tk (Linux) or use the stock Python on macOS/Windows.")

# ── ADB helpers ───────────────────────────────────────────────────────────────

def adb(*args, capture=True) -> subprocess.CompletedProcess:
    """Run an adb command and return the CompletedProcess."""
    cmd = ["adb"] + list(args)
    return subprocess.run(cmd, capture_output=capture, text=True, timeout=30)

def adb_device(*args, serial: str = None) -> subprocess.CompletedProcess:
    """Run an adb command against a specific device serial."""
    prefix = ["-s", serial] if serial else []
    return adb(*prefix, *args)

def detect_device() -> tuple[str | None, str | None]:
    """Return (serial, model) of first connected device, or (None, None)."""
    try:
        result = adb("devices")
        lines  = result.stdout.strip().splitlines()[1:]  # skip header
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                serial = parts[0]
                model_r = adb_device("shell", "getprop", "ro.product.model", serial=serial)
                model = model_r.stdout.strip() if model_r.returncode == 0 else "Unknown"
                return serial, model
    except Exception:
        pass
    return None, None

# ── Installer steps ───────────────────────────────────────────────────────────

STEPS = [
    ("fix_childlock",   "Fix Child Lock / Kids Mode"),
    ("sideload_on",     "Enable sideloading"),
    ("disable_bloat",   "Disable OEM bloatware"),
    ("battery_exempt",  "Battery optimisation exemption"),
    ("install_termux",  "Install Termux + Boot + API"),
    ("bootstrap",       "Bootstrap Termux (Python/ggwave)"),
    ("install_apk",     "Install GibberNode.apk"),
    ("grant_perms",     "Grant runtime permissions"),
    ("boot_script",     "Configure Termux:Boot"),
    ("push_sdcard",     "Push content to SD card"),
    ("verify",          "Verify installation"),
]

BLOATWARE = [
    "com.mediatek.mdmconfig",
    "com.mediatek.mdmloge",
    "com.mediatek.wfo.legacy",
    "com.mediatek.engineermode",
    "com.mediatek.ygps",
    "com.mediatek.mtklogger",
    "com.facebook.appmanager",
    "com.facebook.services",
    "com.google.android.videos",
    "com.google.android.apps.tachyon",
]

SCRIPT_DIR  = Path(__file__).parent
REPO_ROOT   = SCRIPT_DIR.parent.parent


def run_step(serial: str, step: str, apk_path: str, log_q: queue.Queue) -> bool:
    """Execute a single installer step. Returns True on success."""
    def log(msg: str):
        log_q.put(("log", msg))

    def sh(*args):
        return adb_device("shell", *args, serial=serial)

    def pkg_installed(pkg: str) -> bool:
        r = sh(f"pm list packages | grep {pkg}")
        return pkg in r.stdout

    try:
        if step == "fix_childlock":
            sh("am force-stop com.blackview.kidzone")
            sh("settings put secure restricted_profile_id 0")
            sh("pm disable-user --user 0 com.blackview.kidzone")
            sh("pm disable-user --user 0 com.google.android.apps.kids.familylinkhelper")
            log("Kids Mode / restricted profile cleared")

        elif step == "sideload_on":
            sh("settings put global install_non_market_apps 1")
            sh("settings put secure install_non_market_apps 1")
            log("Sideloading enabled")

        elif step == "disable_bloat":
            for pkg in BLOATWARE:
                r = sh(f"pm disable-user --user 0 {pkg}")
                if "disabled" in r.stdout.lower():
                    log(f"  Disabled: {pkg}")

        elif step == "battery_exempt":
            sh("dumpsys deviceidle whitelist +com.termux")
            sh("settings put global background_process_limit 4")
            sh("settings put global app_standby_enabled 0")
            log("Termux exempted from battery optimisation")

        elif step == "install_termux":
            if not pkg_installed("com.termux"):
                log("Termux not found — please install from F-Droid and retry.")
                log("  https://f-droid.org/packages/com.termux/")
                return False
            else:
                log("Termux already installed")

        elif step == "bootstrap":
            cmd = (
                "pkg update -y && pkg upgrade -y && "
                "pkg install -y python python-pip portaudio libzmq git && "
                "pip install ggwave numpy pyaudio requests && "
                "echo BOOTSTRAP_DONE"
            )
            log("Sending bootstrap command to Termux (watch the phone)…")
            sh("am start -n com.termux/.HomeActivity")
            time.sleep(2)
            sh(f'input text "{cmd}"')
            sh("input keyevent 66")
            log("Bootstrap sent — it will run in Termux. Check the phone screen.")

        elif step == "install_apk":
            if not apk_path or not Path(apk_path).exists():
                log("No APK path provided — skip or choose APK file.")
                return False
            result = adb_device("install", "-r", apk_path, serial=serial)
            if result.returncode != 0:
                log(f"APK install failed: {result.stderr[:200]}")
                return False
            log("GibberNode.apk installed")

        elif step == "grant_perms":
            perms = [
                "android.permission.RECORD_AUDIO",
                "android.permission.ACCESS_FINE_LOCATION",
                "android.permission.ACCESS_COARSE_LOCATION",
            ]
            for perm in perms:
                sh(f"pm grant com.axiomzero.pentacorder {perm}")
                log(f"  Granted: {perm}")

        elif step == "boot_script":
            boot_src = SCRIPT_DIR / "termux_boot.sh"
            if boot_src.exists():
                adb_device("push", str(boot_src), "/sdcard/start-gibberlink.sh", serial=serial)
                sh("mkdir -p ~/.termux/boot && cp /sdcard/start-gibberlink.sh ~/.termux/boot/ && chmod +x ~/.termux/boot/start-gibberlink.sh")
                log("Boot script installed")
            else:
                log(f"termux_boot.sh not found at {boot_src}")

        elif step == "push_sdcard":
            manifold = REPO_ROOT / "Unitary-Manifold"
            gibberlink = REPO_ROOT / "Gibberlink"
            if manifold.exists():
                sh("mkdir -p /sdcard/manifold")
                adb_device("push", str(manifold), "/sdcard/manifold/", serial=serial)
                log("Unitary-Manifold pushed to /sdcard/manifold/")
            if gibberlink.exists():
                sh("mkdir -p /sdcard/gibberlink")
                adb_device("push", str(gibberlink), "/sdcard/gibberlink/", serial=serial)
                log("Gibberlink pushed to /sdcard/gibberlink/")

        elif step == "verify":
            termux_ok = pkg_installed("com.termux")
            gibber_ok  = pkg_installed("com.axiomzero.pentacorder")
            log(f"Termux: {'✓ installed' if termux_ok else '✗ NOT found'}")
            log(f"GibberNode: {'✓ installed' if gibber_ok else '✗ NOT installed'}")
            if gibber_ok:
                sh("am start -n com.axiomzero.pentacorder/.MainActivity")
                log("GibberNode launched on device")

        return True

    except subprocess.TimeoutExpired:
        log(f"Step '{step}' timed out")
        return False
    except Exception as e:
        log(f"Step '{step}' error: {e}")
        return False


# ── GUI ───────────────────────────────────────────────────────────────────────

class InstallerGUI:
    def __init__(self, initial_apk: str = ""):
        self.root = tk.Tk()
        self.root.title("GibberNode Installer — BV9900 Pro")
        self.root.resizable(False, False)
        self.root.configure(bg="#0D1117")

        self.serial: str | None = None
        self.model:  str | None = None
        self.log_q:  queue.Queue = queue.Queue()
        self.apk_path = tk.StringVar(value=initial_apk)
        self.step_vars: dict[str, tk.StringVar] = {}
        self.running = False

        self._build_ui()
        self._poll_device()
        self._process_log_queue()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        BG = "#0D1117"; SURFACE = "#161B22"; GREEN = "#00C853"
        RED = "#FF1744"; BLUE = "#2979FF"; FG = "#E6EDF3"; DIM = "#8B949E"
        FONT = ("Consolas", 11)

        pad = dict(padx=12, pady=6)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=GREEN, pady=8)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="GibberNode Installer", font=("Consolas", 16, "bold"),
                 bg=GREEN, fg="#000000").pack()
        tk.Label(hdr, text="Blackview BV9900 Pro — ADB-only, non-destructive",
                 font=FONT, bg=GREEN, fg="#004000").pack()

        # ── Device status bar ─────────────────────────────────────────────────
        dev_row = tk.Frame(self.root, bg=SURFACE, pady=4)
        dev_row.pack(fill=tk.X)
        tk.Label(dev_row, text="Device:", font=FONT, bg=SURFACE, fg=DIM).pack(side=tk.LEFT, padx=12)
        self.device_label = tk.Label(dev_row, text="Scanning…", font=FONT,
                                      bg=SURFACE, fg=FG)
        self.device_label.pack(side=tk.LEFT)

        self.rescan_btn = tk.Button(dev_row, text="Rescan", font=FONT,
                                    bg="#21262D", fg=BLUE, relief=tk.FLAT,
                                    command=self._poll_device)
        self.rescan_btn.pack(side=tk.RIGHT, padx=12)

        # ── APK picker ────────────────────────────────────────────────────────
        apk_row = tk.Frame(self.root, bg=BG, pady=4)
        apk_row.pack(fill=tk.X, padx=12)
        tk.Label(apk_row, text="GibberNode APK:", font=FONT, bg=BG, fg=DIM).pack(side=tk.LEFT)
        tk.Entry(apk_row, textvariable=self.apk_path, font=FONT, bg=SURFACE,
                 fg=FG, insertbackground=FG, width=42).pack(side=tk.LEFT, padx=8)
        tk.Button(apk_row, text="Browse…", font=FONT, bg="#21262D", fg=BLUE,
                  relief=tk.FLAT, command=self._pick_apk).pack(side=tk.LEFT)

        # ── Steps grid ────────────────────────────────────────────────────────
        steps_frame = tk.Frame(self.root, bg=SURFACE, pady=8, padx=12)
        steps_frame.pack(fill=tk.X, padx=12, pady=4)
        tk.Label(steps_frame, text="Installation Steps", font=("Consolas", 12, "bold"),
                 bg=SURFACE, fg=GREEN).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=4)

        for idx, (key, label) in enumerate(STEPS, start=1):
            var = tk.StringVar(value="○")
            self.step_vars[key] = var
            tk.Label(steps_frame, textvariable=var, font=FONT, bg=SURFACE,
                     fg=DIM, width=3).grid(row=idx, column=0, sticky=tk.W)
            tk.Label(steps_frame, text=label, font=FONT, bg=SURFACE,
                     fg=FG, anchor=tk.W).grid(row=idx, column=1, sticky=tk.W, padx=8)

        # ── Action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self.root, bg=BG, pady=8)
        btn_frame.pack(fill=tk.X, padx=12)

        def btn(parent, label, color, cmd):
            return tk.Button(parent, text=label, font=FONT, bg=color, fg="#000",
                             relief=tk.FLAT, padx=12, pady=6, command=cmd)

        btn(btn_frame, "▶  Run All Steps", GREEN,
            self._run_all).pack(side=tk.LEFT, padx=(0, 8))
        btn(btn_frame, "Fix Child Lock",  RED,
            lambda: self._run_single("fix_childlock")).pack(side=tk.LEFT, padx=(0, 8))
        btn(btn_frame, "Install Termux",  BLUE,
            lambda: self._run_single("install_termux")).pack(side=tk.LEFT, padx=(0, 8))
        btn(btn_frame, "Install APK",     "#FFAB00",
            lambda: self._run_single("install_apk")).pack(side=tk.LEFT, padx=(0, 8))
        btn(btn_frame, "Config Boot",     "#8B00FF",
            lambda: self._run_single("boot_script")).pack(side=tk.LEFT)

        # ── Progress bar ──────────────────────────────────────────────────────
        self.progress = ttk.Progressbar(self.root, mode="determinate",
                                        maximum=len(STEPS), length=560)
        self.progress.pack(padx=12, pady=(4, 0), fill=tk.X)

        # ── Log console ───────────────────────────────────────────────────────
        self.log_text = scrolledtext.ScrolledText(
            self.root, font=("Consolas", 10), bg="#000000", fg=GREEN,
            insertbackground=GREEN, height=14, width=72,
        )
        self.log_text.pack(padx=12, pady=8, fill=tk.BOTH)
        self.log_text.config(state=tk.DISABLED)

    # ── Actions ────────────────────────────────────────────────────────────────

    def _pick_apk(self):
        path = filedialog.askopenfilename(
            title="Select GibberNode APK",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")],
        )
        if path:
            self.apk_path.set(path)

    def _run_all(self):
        if self.running: return
        self._reset_steps()
        threading.Thread(target=self._worker,
                         args=([k for k, _ in STEPS],), daemon=True).start()

    def _run_single(self, step_key: str):
        if self.running: return
        threading.Thread(target=self._worker, args=([step_key],), daemon=True).start()

    def _worker(self, steps: list[str]):
        self.running = True
        self._log("\n── Starting installer ──────────────────────────────────")
        completed = 0
        for step_key in steps:
            self.step_vars[step_key].set("⟳")
            self._log(f"\n[STEP] {dict(STEPS).get(step_key, step_key)}")
            ok = run_step(
                serial   = self.serial or "",
                step     = step_key,
                apk_path = self.apk_path.get(),
                log_q    = self.log_q,
            )
            self.step_vars[step_key].set("✓" if ok else "✗")
            completed += 1
            self.log_q.put(("progress", completed))

        self._log("\n── Done ──────────────────────────────────────────────")
        self.running = False

    # ── Device polling ─────────────────────────────────────────────────────────

    def _poll_device(self):
        def _check():
            serial, model = detect_device()
            self.serial = serial
            self.model  = model
            if serial:
                self.device_label.config(
                    text=f"✓  {model}  ({serial})", fg="#00C853"
                )
            else:
                self.device_label.config(
                    text="⚠  No device detected — connect via USB", fg="#FF1744"
                )
        threading.Thread(target=_check, daemon=True).start()

    # ── Log queue processing ───────────────────────────────────────────────────

    def _process_log_queue(self):
        try:
            while True:
                item = self.log_q.get_nowait()
                kind, value = item
                if kind == "log":
                    self._log(value)
                elif kind == "progress":
                    self.progress["value"] = value
        except queue.Empty:
            pass
        self.root.after(100, self._process_log_queue)

    def _log(self, msg: str):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _reset_steps(self):
        for var in self.step_vars.values():
            var.set("○")
        self.progress["value"] = 0

    def run(self):
        self.root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="GibberNode GUI Installer for BV9900 Pro")
    parser.add_argument("--apk", default="", help="Path to GibberNode.apk")
    args = parser.parse_args()
    InstallerGUI(initial_apk=args.apk).run()


if __name__ == "__main__":
    main()
