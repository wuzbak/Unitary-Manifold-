# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Bounded subprocesses with live log streaming and process-group cleanup."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from contextlib import ExitStack
from pathlib import Path

from .evidence import write_json


def discard_scratch(directory: Path) -> None:
    """Remove temporary artifacts without following links or retaining frozen copies."""
    if directory.is_symlink():
        directory.unlink()
    elif directory.exists():
        for _, _, _, descriptor in os.fwalk(directory, follow_symlinks=False):
            os.fchmod(descriptor, 0o700)
        shutil.rmtree(directory)


def execute(command: list[str], cwd: Path, directory: Path, timeout: float,
            environment: dict | None = None, *, stream: bool = True,
            separate_stderr: bool = False) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    result = {"command": command, "cwd": str(cwd), "returncode": None,
              "timed_out": False, "error": None}
    process = None
    readers = []
    with ExitStack() as stack:
        log = stack.enter_context((directory / "output.log").open("xb"))
        error_log = stack.enter_context((directory / "stderr.log").open("xb")) \
            if separate_stderr else log
        try:
            process = subprocess.Popen(
                command, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE if separate_stderr else subprocess.STDOUT,
                start_new_session=True,
            )

            def copy_output(source, destination):
                while chunk := source.read1(65536):
                    destination.write(chunk)
                    destination.flush()
                    if stream:
                        try:
                            sys.stderr.write(chunk.decode("utf-8", errors="replace"))
                            sys.stderr.flush()
                        except (OSError, ValueError):
                            pass

            for source, destination in [(process.stdout, log), (process.stderr, error_log)]:
                if source is not None:
                    reader = threading.Thread(target=copy_output, args=(source, destination), daemon=True)
                    reader.start()
                    readers.append(reader)
            try:
                result["returncode"] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                result["timed_out"] = True
            except KeyboardInterrupt:
                result["error"] = "interrupted"
        except OSError as exc:
            result["error"] = str(exc)
        finally:
            if process is not None:
                # Clean descendants even when the leader exited normally; descendants
                # may otherwise hold the output pipe open indefinitely.
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                result["returncode"] = process.wait(timeout=5)
                for reader in readers:
                    reader.join(timeout=5)
                    if reader.is_alive():
                        result["error"] = "output stream did not close after process cleanup"
                for source in [process.stdout, process.stderr]:
                    if source:
                        source.close()
    result["seconds"] = time.monotonic() - start
    write_json(directory / "process.json", result)
    return result
