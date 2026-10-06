# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Loopback-only, offline operational UI over a serialized evidence task queue."""

from __future__ import annotations

import fcntl
import importlib.util
import ipaddress
import json
import queue
import re
import secrets
import shutil
import socket
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from . import VERSION, engine
from .adapters import load_config, selection_policy
from .evidence import EvidenceError, canonical, contained, read_json
from .reporting import report

MAX_BODY = 4096
MAX_LOG = 64 * 1024
MAX_QUEUE = 32
IDENTIFIER = re.compile(r"[0-9a-f]{32}")
STATIC = Path(__file__).resolve().parent / "static"


def identifier(value: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise EvidenceError("Expected an artifact/task ID, not a filesystem path")
    return value


class Application:
    """Only startup-selected roots/configuration can enter the execution engine."""

    def __init__(self, root: Path, store: Path, config: Path | None = None,
                 adapter: str = "um", mode: str = "full"):
        self.root, self.store = root.resolve(), store.resolve()
        self.config = config.resolve() if config else None
        self.adapter, self.mode = adapter, mode
        if not self.root.is_dir() or self.root.is_relative_to(self.store):
            raise EvidenceError("Select an existing repository and a separate artifact store")
        load_config(self.root, self.config, self.adapter)
        selection_policy(mode)
        self.store.mkdir(parents=True, exist_ok=True)
        self._lease = contained(self.store, ".server.lock", must_exist=False).open("a+b")
        started = False
        try:
            try:
                fcntl.flock(self._lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise EvidenceError("Another UM-ARTS server owns this artifact store") from exc
            contained(self.store, "tasks", must_exist=False).mkdir(exist_ok=True)
            self.token = secrets.token_urlsafe(32)
            self.lock = threading.RLock()
            self.pending = queue.Queue(maxsize=MAX_QUEUE)
            self.active = None
            self.before = {}
            self.stopping = False
            # Recovery is allowed only while holding the store's exclusive lifecycle lease.
            for task in self.tasks():
                if task["status"] in {"queued", "running"}:
                    task.update(status="incomplete", error="Server stopped before task completion")
                    self._save(task)
                    self._log(task["id"], "Interrupted server session; not automatically resumed")
            self.worker = threading.Thread(target=self._work, name="um-arts-queue", daemon=True)
            self.worker.start()
            started = True
        finally:
            if not started:
                self._lease.close()

    def _task_path(self, task_id: str, suffix: str = "json") -> Path:
        return contained(self.store, f"tasks/{identifier(task_id)}.{suffix}", must_exist=False)

    def _save(self, task: dict) -> None:
        with self.lock:
            path = self._task_path(task["id"])
            staging = self._task_path(task["id"], "next")
            with staging.open("wb") as stream:
                stream.write(canonical(task))
            staging.replace(path)

    def _log(self, task_id: str, message: str) -> None:
        with self.lock, self._task_path(task_id, "log").open("a", encoding="utf-8") as stream:
            stream.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {message}\n")

    def task(self, task_id: str) -> dict:
        with self.lock:
            return read_json(contained(self.store, f"tasks/{identifier(task_id)}.json"))

    def tasks(self) -> list[dict]:
        directory = contained(self.store, "tasks", must_exist=False)
        if not directory.is_dir():
            return []
        with self.lock:
            result = [self.task(path.stem) for path in directory.glob("*.json")
                      if IDENTIFIER.fullmatch(path.stem)]
        return sorted(result, key=lambda item: item["created"], reverse=True)

    def artifact_path(self, kind: str, artifact_id: str) -> Path:
        if kind not in {"plans", "attempts", "imports"}:
            raise EvidenceError("Unknown artifact kind")
        directory = contained(self.store, f"{kind}/{identifier(artifact_id)}", must_exist=False)
        if not directory.is_dir():
            raise EvidenceError("Artifact does not exist")
        return directory

    def _artifact_ids(self, kind: str) -> set[str]:
        directory = contained(self.store, kind, must_exist=False)
        if not directory.is_dir():
            return set()
        return {p.name for p in directory.iterdir()
                if IDENTIFIER.fullmatch(p.name) and not p.is_symlink() and p.is_dir()}

    def inspect(self, kind: str, artifact_id: str) -> dict:
        directory = self.artifact_path(kind, artifact_id)
        if kind in {"attempts", "imports"}:
            return report(directory)
        engine.verify_seal(directory)
        spec = read_json(contained(directory, "plan.json"))
        return {key: spec.get(key) for key in
                ("status", "errors", "selection", "suites", "jobs", "formal")}

    def artifacts(self) -> list[dict]:
        result = []
        for kind in ("plans", "attempts", "imports"):
            for artifact_id in sorted(self._artifact_ids(kind), reverse=True):
                directory = self.artifact_path(kind, artifact_id)
                # Listing does not assert validation; inspect/report is the evidence gate.
                captured = (directory / "capture.json").is_file()
                metadata = ("plan.json" if kind == "plans" else "capture.json" if captured
                            else "attempt.json")
                try:
                    spec = read_json(contained(directory, metadata))
                    status = spec.get("status", "unverified")
                except (EvidenceError, AttributeError):
                    status = "incomplete"
                result.append({"kind": kind, "id": artifact_id, "status": status,
                               "verified": False, "evidence_kind": "capture" if captured else kind,
                               "resumable": kind == "attempts" and not captured})
        return result

    def _trusted_plan(self, directory: Path) -> None:
        spec = engine.validate_plan(directory)
        source = spec.get("config_source")
        if spec.get("root") != str(self.root) or spec.get("store") != str(self.store) \
                or spec.get("config") != load_config(self.root, self.config, self.adapter) \
                or (source.get("path") if isinstance(source, dict) else None) != (
                    str(self.config) if self.config else None):
            raise EvidenceError("Artifact does not use the server's trusted execution inputs")

    def submit(self, payload: dict) -> dict:
        action = payload.get("action")
        if action not in {"plan", "run", "resume"}:
            raise EvidenceError("Only plan, run, and resume are supported")
        expected = {"action"} if action == "plan" else {"action", "id"}
        if set(payload) != expected:
            raise EvidenceError("Unexpected request settings; execution inputs are startup-only")
        artifact_id = None if action == "plan" else identifier(payload["id"])
        if artifact_id:
            directory = self.artifact_path("plans" if action == "run" else "attempts", artifact_id)
            if action == "resume" and (directory / "capture.json").exists():
                raise EvidenceError("Captured bundles are read-only and cannot be resumed")
            self._trusted_plan(directory if action == "run" else directory / "plan")
        with self.lock:
            if self.stopping or self.pending.full():
                raise EvidenceError("Task queue is full or shutting down")
            task = {"id": uuid.uuid4().hex, "action": action, "artifact_id": artifact_id,
                    "status": "queued", "created": time.time(), "result": None}
            self._save(task)
            self._log(task["id"], f"Queued {action}; no pass inferred")
            self.pending.put_nowait(task["id"])
        return task

    def _work(self) -> None:
        while True:
            task_id = self.pending.get()
            try:
                if task_id is None:
                    return
                task = self.task(task_id)
                with self.lock:
                    self.active = task_id
                    self.before = {kind: self._artifact_ids(kind) for kind in ("plans", "attempts")}
                    task.update(status="running", started=time.time())
                    self._save(task)
                self._log(task_id, f"Starting {task['action']}")
                try:
                    if task["action"] == "plan":
                        result = engine.plan(self.root, self.store, self.config, self.adapter, self.mode)
                    else:
                        kind = "plans" if task["action"] == "run" else "attempts"
                        directory = self.artifact_path(kind, task["artifact_id"])
                        self._trusted_plan(directory if kind == "plans" else directory / "plan")
                        result = (engine.run(contained(directory, "plan.json")) if kind == "plans"
                                  else engine.resume(directory))
                    if not isinstance(result, dict) or result.get("status") not in {
                            "ready", "passed", "blocked", "incomplete"}:
                        raise EvidenceError("Engine returned no recognized evidence status")
                    task.update(status=result["status"], result=result)
                    for key, kind in (("plan_path", "plans"), ("attempt_path", "attempts")):
                        if key in result:
                            path = Path(result[key])
                            artifact_id = path.parent.name if key == "plan_path" else path.name
                            self.artifact_path(kind, artifact_id)
                            task["artifact"] = {"kind": kind, "id": artifact_id}
                except Exception as exc:  # noqa: BLE001 -- Persist failures without terminating the queue.
                    task.update(status="blocked", error=f"{type(exc).__name__}: {exc}")
                task["finished"] = time.time()
                self._log(task_id, f"Finished with evidence status: {task['status']}")
                with self.lock:
                    self._save(task)
                    self.active = None
                    self.before = {}
            finally:
                self.pending.task_done()

    def _tail(self, path: Path) -> str:
        with path.open("rb") as stream:
            stream.seek(0, 2)
            stream.seek(max(0, stream.tell() - MAX_LOG))
            return stream.read(MAX_LOG).decode("utf-8", errors="replace")

    def artifact_logs(self, kind: str, artifact_id: str) -> str:
        directory = self.artifact_path(kind, artifact_id)
        chunks = []
        # Only engine-created stdout/stderr files, never arbitrary client paths.
        for name in ("output.log", "stderr.log"):
            for path in sorted(directory.rglob(name)):
                checked = contained(directory, path.relative_to(directory).as_posix())
                chunks.append(f"\n--- {path.relative_to(directory)} ---\n{self._tail(checked)}")
                if sum(map(len, chunks)) >= MAX_LOG:
                    return "".join(chunks)[-MAX_LOG:]
        return "".join(chunks)[-MAX_LOG:]

    def logs(self, task_id: str) -> str:
        task = self.task(task_id)
        text = self._tail(contained(self.store, f"tasks/{identifier(task_id)}.log"))
        artifacts = [task["artifact"]] if task.get("artifact") else []
        with self.lock:
            if self.active == task_id:
                artifacts = [{"kind": kind, "id": item}
                             for kind in ("plans", "attempts")
                             for item in self._artifact_ids(kind) - self.before.get(kind, set())]
        for artifact in artifacts:
            text += self.artifact_logs(artifact["kind"], artifact["id"])
        return text[-MAX_LOG:]

    def preflight(self) -> dict:
        tools = {"python": True, "pytest": importlib.util.find_spec("pytest") is not None,
                 "git": shutil.which("git") is not None,
                 "lean": shutil.which("lean") is not None, "lake": shutil.which("lake") is not None}
        config = load_config(self.root, self.config, self.adapter)
        ready = tools["pytest"] and (not config["lean"] or (tools["lean"] and tools["lake"]))
        return {"status": "ready" if ready else "blocked", "tools": tools,
                "root": str(self.root), "store": str(self.store), "adapter": config["adapter"],
                "selection": selection_policy(self.mode),
                "boundary": "Tool availability only, not regression evidence or formal correspondence"}

    def close(self) -> None:
        with self.lock:
            if self.stopping:
                return
            self.stopping = True
        self.pending.put(None)
        self.worker.join()
        # Keep the lock inode in place; unlinking would let a second daemon bypass it.
        self._lease.close()


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, app: Application, host: str = "127.0.0.1", port: int = 8765):
        host = "127.0.0.1" if host == "localhost" else host
        try:
            address = ipaddress.ip_address(host)
        except ValueError as exc:
            raise EvidenceError("Server host must be a numeric loopback address or localhost") from exc
        if not address.is_loopback:
            raise EvidenceError("Remote binding is disabled; use a loopback address")
        self.address_family = socket.AF_INET6 if address.version == 6 else socket.AF_INET
        self.app = app
        super().__init__((host, port), Handler)
        actual_port = self.server_address[1]
        authority = f"[{host}]" if address.version == 6 else host
        self.authorities = {f"{authority}:{actual_port}", f"localhost:{actual_port}"}
        self.url = f"http://{authority}:{actual_port}"


class Handler(BaseHTTPRequestHandler):
    server: LocalServer

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *args) -> None:
        pass

    def _reply(self, status: int, data, content_type: str = "application/json") -> None:
        body = canonical(data) if content_type == "application/json" else data
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'self'; style-src 'self'; "
                         "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _boundary(self) -> bool:
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        if len(hosts) != 1 or hosts[0] not in self.server.authorities \
                or len(origins) > 1 or (origins and origins[0] != "http://" + hosts[0]) \
                or self.headers.get("Sec-Fetch-Site") not in {None, "same-origin", "none"}:
            self._reply(403, {"error": "Only same-origin loopback requests are allowed"})
            return False
        return True

    def do_GET(self) -> None:
        if not self._boundary():
            return
        app = self.server.app
        try:
            parsed = urlsplit(self.path)
            if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
                raise EvidenceError("Unsupported URL")
            path = parsed.path
            static = {"/": ("index.html", "text/html; charset=utf-8"),
                      "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                      "/style.css": ("style.css", "text/css; charset=utf-8")}
            if path in static:
                name, mime = static[path]
                self._reply(200, contained(STATIC, name).read_bytes(), mime)
                return
            if path == "/api/health":
                result = {"status": "ok", "version": VERSION, "active_task": app.active}
            elif path == "/api/session":
                result = {"token": app.token}
            elif path == "/api/preflight":
                result = app.preflight()
            elif path == "/api/tasks":
                result = app.tasks()
            elif path == "/api/artifacts":
                result = app.artifacts()
            else:
                parts = path.strip("/").split("/")
                if len(parts) in {3, 4} and parts[:2] == ["api", "tasks"]:
                    result = ({"text": app.logs(parts[2])} if len(parts) == 4 and parts[3] == "logs"
                              else app.task(parts[2]) if len(parts) == 3 else None)
                elif len(parts) in {4, 5} and parts[:2] == ["api", "artifacts"]:
                    result = ({"text": app.artifact_logs(parts[2], parts[3])}
                              if len(parts) == 5 and parts[4] == "logs"
                              else app.inspect(parts[2], parts[3]) if len(parts) == 4 else None)
                else:
                    result = None
                if result is None:
                    self._reply(404, {"error": "Unknown endpoint"})
                    return
            self._reply(200, result)
        except (EvidenceError, ValueError, OSError, KeyError, TypeError) as exc:
            self._reply(400, {"error": str(exc)})

    def do_POST(self) -> None:
        self.close_connection = True
        if not self._boundary():
            return
        tokens = self.headers.get_all("X-UM-ARTS-Token", [])
        if len(tokens) != 1 or not tokens[0].isascii() \
                or not secrets.compare_digest(tokens[0], self.server.app.token):
            self._reply(403, {"error": "Session token required"})
            return
        if self.path != "/api/tasks":
            self._reply(404, {"error": "Unknown endpoint"})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if self.headers.get("Transfer-Encoding") or len(lengths) != 1 \
                or not re.fullmatch(r"[0-9]{1,8}", lengths[0]):
            self._reply(400, {"error": "A single bounded Content-Length is required"})
            return
        size = int(lengths[0])
        if size > MAX_BODY:
            self._reply(413, {"error": "Request exceeds 4096 bytes"})
            return
        if self.headers.get("Content-Type") != "application/json":
            self._reply(415, {"error": "application/json required"})
            return
        try:
            body = self.rfile.read(size)
            if len(body) != size:
                raise EvidenceError("Truncated request")

            def pairs(items):
                value = {}
                for key, item in items:
                    if key in value:
                        raise EvidenceError("Duplicate JSON key")
                    value[key] = item
                return value

            def reject_constant(value):
                raise EvidenceError("Nonfinite JSON is not allowed")

            payload = json.loads(body, object_pairs_hook=pairs, parse_constant=reject_constant)
            if not isinstance(payload, dict):
                raise EvidenceError("Request must be a JSON object")
            result = self.server.app.submit(payload)
            self._reply(202, result)
        except (EvidenceError, ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
            self._reply(400, {"error": str(exc)})


def serve(root: Path, store: Path, config: Path | None = None, adapter: str = "um",
          mode: str = "full", host: str = "127.0.0.1", port: int = 8765) -> int:
    app = Application(root, store, config, adapter, mode)
    try:
        server = LocalServer(app, host, port)
        print(f"UM-ARTS local dashboard: {server.url}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    finally:
        app.close()
    return 0
