# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "06-omega-synthesis"))

from library_console import Workbench, make_handler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402


def _server():
    bench = Workbench("omega", "Omega", Path(__file__).resolve().parents[2] / "06-omega-synthesis")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(bench, 0))
    port = httpd.server_address[1]
    httpd.RequestHandlerClass = make_handler(bench, port)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def _post(port, headers):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/call", data=b"{}", method="POST",
        headers={"Content-Type": "application/json", **headers})
    try:
        return urllib.request.urlopen(req, timeout=10).status
    except urllib.error.HTTPError as err:
        return err.code


def test_health_and_post_guards():
    httpd, port = _server()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=10) as r:
            assert json.load(r)
        assert _post(port, {}) == 403
        assert _post(port, {"X-Console": "1", "Host": "evil.example"}) == 403
    finally:
        httpd.shutdown()


@pytest.mark.parametrize(
    ("product", "module", "database", "operation"),
    [
        ("08-axiom-journalist", "app.db.cases", "axiom_cases.db",
         "m.create_case('Case', 'Lead'); assert m.list_cases()[0]['title'] == 'Case'"),
        ("09-omegaholon", "app.db.tracker", "omegaholon.db",
         "m.get_or_create_profile('Profile'); assert m.list_profiles()[0]['name'] == 'Profile'"),
        ("16-oracle", "oracle.db.store", "oracle.db", "m.init_db()"),
    ],
)
def test_product_databases_use_suite_data_directory(tmp_path, product, module, database, operation):
    root = Path(__file__).resolve().parents[2] / product
    data = tmp_path / product
    script = (
        f"import importlib; m = importlib.import_module({module!r}); "
        f"m.init_db(); {operation}; assert m.DB_PATH.name == {database!r}"
    )
    subprocess.run(
        [sys.executable, "-c", script],
        cwd=root,
        env={**os.environ, "AZ_PRODUCT_DATA": str(data)},
        check=True,
    )
    assert (data / database).is_file()
