# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Loopback, stdlib-only workbench for AZ-IP products that ship as Python packages.

It lists a package's modules, shows public constants/callables with signatures and
docstrings, and runs a chosen public function or class method with JSON arguments.
Results are raw outputs of the product code; the console adds no scientific claim.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import inspect
import json
import pkgutil
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MAX_BODY = 1 << 20
MAX_RESULT_CHARS = 200_000
CALL_TIMEOUT_SECONDS = 120

_PAGE = (Path(__file__).with_name("index.html")).read_text(encoding="utf-8") if Path(__file__).with_name("index.html").exists() else ""


def _jsonable(value, depth=0):
    if depth > 8:
        return repr(value)[:200]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _jsonable(dataclasses.asdict(value), depth + 1)
    if isinstance(value, dict):
        return {str(k): _jsonable(v, depth + 1) for k, v in list(value.items())[:500]}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v, depth + 1) for v in list(value)[:500]]
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        try:
            return _jsonable(tolist(), depth + 1)
        except Exception:
            pass
    return repr(value)[:2000]


class Workbench:
    def __init__(self, package: str, title: str, readme: Path | None):
        self.package = package
        self.title = title
        self.readme = readme
        self.root = importlib.import_module(package)

    def modules(self) -> list[dict]:
        names = [self.package]
        path = getattr(self.root, "__path__", None)
        if path:
            names += [m.name for m in pkgutil.walk_packages(path, self.package + ".")]
        rows = []
        for name in names:
            try:
                mod = importlib.import_module(name)
                rows.append({"name": name, "importable": True, "doc": (inspect.getdoc(mod) or "").split("\n\n")[0][:300]})
            except BaseException as error:  # missing optional dependency, etc.
                rows.append({"name": name, "importable": False, "error": f"{type(error).__name__}: {error}"[:300]})
        return rows

    def _module(self, name: str):
        if name != self.package and not name.startswith(self.package + "."):
            raise ValueError("Module is outside the product package.")
        return importlib.import_module(name)

    def describe(self, name: str) -> dict:
        mod = self._module(name)
        constants, callables = {}, []
        exported = getattr(mod, "__all__", None)
        for attr in sorted(exported if exported is not None else dir(mod)):
            if attr.startswith("_") or not hasattr(mod, attr):
                continue
            obj = getattr(mod, attr)
            if inspect.isclass(obj) or inspect.isfunction(obj):
                if exported is None and getattr(obj, "__module__", None) != mod.__name__:
                    continue
                try:
                    signature = str(inspect.signature(obj))
                except (TypeError, ValueError):
                    signature = "(...)"
                entry = {"name": attr, "kind": "class" if inspect.isclass(obj) else "function",
                         "signature": signature, "doc": (inspect.getdoc(obj) or "")[:600]}
                if inspect.isclass(obj):
                    entry["methods"] = [
                        {"name": m, "signature": str(inspect.signature(f)) if callable(f) else "()"}
                        for m, f in inspect.getmembers(obj, inspect.isfunction) if not m.startswith("_")
                    ][:40]
                callables.append(entry)
            elif isinstance(obj, (int, float, str, bool)) and attr.isupper():
                constants[attr] = obj
        return {"name": mod.__name__, "doc": inspect.getdoc(mod) or "", "constants": constants, "callables": callables}

    def call(self, request: dict) -> dict:
        mod = self._module(str(request.get("module", "")))
        target = getattr(mod, str(request.get("name", "")), None)
        if target is None or str(request["name"]).startswith("_") or not (inspect.isfunction(target) or inspect.isclass(target)):
            raise ValueError("Unknown public callable.")
        args, kwargs = request.get("args", []), request.get("kwargs", {})
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            raise ValueError("args must be a list and kwargs an object.")
        method = request.get("method")
        outcome: dict = {}

        def run():
            try:
                if inspect.isclass(target):
                    instance = target(*request.get("init_args", []), **request.get("init_kwargs", {}))
                    if method:
                        if str(method).startswith("_") or not callable(getattr(instance, str(method), None)):
                            raise ValueError("Unknown public method.")
                        outcome["value"] = getattr(instance, str(method))(*args, **kwargs)
                    else:
                        outcome["value"] = instance
                else:
                    outcome["value"] = target(*args, **kwargs)
            except BaseException as error:
                outcome["error"] = f"{type(error).__name__}: {error}"[:2000]

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        worker.join(CALL_TIMEOUT_SECONDS)
        if worker.is_alive():
            return {"ok": False, "error": f"Call exceeded {CALL_TIMEOUT_SECONDS}s and was abandoned."}
        if "error" in outcome:
            return {"ok": False, "error": outcome["error"]}
        text = json.dumps(_jsonable(outcome["value"]), indent=2)
        return {"ok": True, "result": text[:MAX_RESULT_CHARS], "truncated": len(text) > MAX_RESULT_CHARS}


def make_handler(bench: Workbench, port: int):
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, payload) -> None:
            self._send(status, json.dumps(payload).encode("utf-8"))

        def _guard(self) -> bool:
            if self.headers.get("Host", "") not in allowed_hosts:
                self._json(403, {"error": "Unexpected Host header."})
                return False
            return True

        def do_GET(self):
            if not self._guard():
                return
            url = urlparse(self.path)
            query = parse_qs(url.query)
            try:
                if url.path in ("/", "/index.html"):
                    self._send(200, _PAGE.replace("{{TITLE}}", bench.title).encode("utf-8"), "text/html")
                elif url.path == "/api/health":
                    self._json(200, {"status": "ok", "package": bench.package})
                elif url.path == "/api/modules":
                    self._json(200, {"title": bench.title, "package": bench.package, "modules": bench.modules()})
                elif url.path == "/api/module":
                    self._json(200, bench.describe(query.get("name", [""])[0]))
                elif url.path == "/api/readme":
                    text = bench.readme.read_text(encoding="utf-8", errors="replace") if bench.readme and bench.readme.is_file() else ""
                    self._json(200, {"text": text[:200_000]})
                else:
                    self._json(404, {"error": "Not found."})
            except Exception as error:
                self._json(400, {"error": f"{type(error).__name__}: {error}"[:500]})

        def do_POST(self):
            if not self._guard():
                return
            if self.path != "/api/call" or self.headers.get("X-Console") != "1":
                self._json(403, {"error": "Forbidden."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY:
                    raise ValueError("Request body size is invalid.")
                self._json(200, bench.call(json.loads(self.rfile.read(length))))
            except Exception as error:
                self._json(400, {"ok": False, "error": f"{type(error).__name__}: {error}"[:500]})

    return Handler


def serve(package: str, title: str, product_root: Path, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Serve the {title} workbench on loopback.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args(argv)
    if args.host not in ("127.0.0.1", "localhost"):
        parser.error("The workbench only binds to loopback.")
    sys.path.insert(0, str(product_root))
    bench = Workbench(package, title, product_root / "README.md")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(bench, args.port))
    print(f"{title} workbench: http://{args.host}:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0
