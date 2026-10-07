# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Bounded, non-executing canonical AST facts and sealed incremental artifacts."""

import hashlib
import json
import shutil
import sqlite3
import uuid
from pathlib import Path

import pytest
from TOOLS.um_arts.evidence import EvidenceError, seal, verify_seal

from TOOLS.um_arts import code_index


@pytest.fixture
def index_work():
    work = Path.cwd() / ".um-arts-test-work" / uuid.uuid4().hex
    root = work / "source"
    root.mkdir(parents=True)
    yield root, work
    shutil.rmtree(work)


def put(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)
    return path


def test_canonical_facts_scopes_and_no_source_execution(index_work):
    root, work = index_work
    marker = root / "executed"
    source = (
        "import os as system\nfrom .helpers import run as execute\n"
        f"open({str(marker)!r}, 'w').write('executed')\n"
        "@decorate()\nclass Worker(base()):\n"
        "    def run(self, value=default()):\n"
        "        def nested():\n"
        "            engine.execute(value)\n"
        "            factory()()\n"
        "        nested()\n"
    )
    put(root, "pkg/main.py", source)
    put(root, ".github/agents/ignored.py", "raise RuntimeError('ignored')")
    (root / "alias.py").symlink_to("pkg/main.py")
    result = code_index.build_index(root, work / "index")
    verify_seal(work / "index")
    assert result["status"] == "indexed"
    assert result["counts"]["files"] == result["counts"]["parsed"] == 1
    assert result["counts"]["imports"] == 2
    assert result["counts"]["declarations"] == 3
    assert not marker.exists()
    files = code_index.query_index(work / "index", "files")["rows"]
    assert files[0]["path"] == "pkg/main.py"
    assert files[0]["sha256"] == hashlib.sha256(source.encode()).hexdigest()
    imports = code_index.query_index(work / "index", "imports")["rows"]
    assert {(item["name"], item["detail"]) for item in imports} == {
        ("os", "system"), (".helpers.run", "execute"),
    }
    declarations = code_index.query_index(work / "index", "declarations")["rows"]
    assert declarations[-1]["qualified_symbol"] == "pkg.main.Worker.run.nested"
    calls = code_index.query_index(work / "index")["rows"]
    execute = next(row for row in calls if row["name"] == "engine.execute")
    assert execute["line"] == 8
    assert execute["qualified_symbol"] == "pkg.main.Worker.run.nested"
    assert all(row["resolution"] == "unresolved" for row in calls)
    assert any(row["name"] == "<dynamic>" for row in calls)
    assert next(row for row in calls if row["name"] == "decorate")["qualified_symbol"] == "pkg.main"
    assert next(row for row in calls if row["name"] == "default")["qualified_symbol"] == "pkg.main.Worker"
    assert result["proof_claim"] is result["security_certification"] is False
    assert "taint" in " ".join(result["boundaries"])


def test_incremental_changed_deleted_and_reused(index_work, monkeypatch):
    root, work = index_work
    put(root, "stable.py", "stable()\n")
    changed = put(root, "changed.py", "old()\n")
    deleted = put(root, "deleted.py", "gone()\n")
    code_index.build_index(root, work / "first")
    changed.write_text("new()\n")
    deleted.unlink()
    put(root, "added.py", "added()\n")
    original = code_index.ast.parse
    parsed = []

    def track(data, filename):
        parsed.append(filename)
        return original(data, filename=filename)

    monkeypatch.setattr(code_index.ast, "parse", track)
    result = code_index.build_index(root, work / "second", work / "first")
    assert result["status"] == "indexed"
    assert result["counts"]["files"] == 3 and result["counts"]["reused"] == 1
    assert sorted(parsed) == ["added.py", "changed.py"]
    rows = code_index.query_index(work / "second")["rows"]
    assert {row["name"] for row in rows} == {"stable", "new", "added"}
    assert code_index.query_index(work / "first")["rows"][1]["name"] == "gone"
    assert verify_seal(work / "first")


def test_output_nested_in_previous_is_rejected_without_mutation(index_work):
    root, work = index_work
    put(root, "stable.py", "stable()\n")
    first = work / "first"
    code_index.build_index(root, first)
    before = {path.name: path.read_bytes() for path in first.iterdir()}
    with pytest.raises(EvidenceError, match="previous sealed artifact"):
        code_index.build_index(root, first / "nested" / "second", first)
    assert before == {path.name: path.read_bytes() for path in first.iterdir()}
    assert not (first / "nested").exists()
    assert verify_seal(first)


@pytest.mark.parametrize("field", ["code_sha256", "python_version"])
def test_extraction_identity_changes_force_reparse(index_work, monkeypatch, field):
    root, work = index_work
    put(root, "stable.py", "stable()\n")
    first = work / "first"
    original = code_index.build_index(root, first)
    identity = original["extraction_identity"]
    assert identity["code_sha256"] == hashlib.sha256(Path(code_index.__file__).read_bytes()).hexdigest()
    assert identity["python_version"] == code_index.sys.version
    metadata = first / "code_index.json"
    stale = json.loads(metadata.read_text())
    stale["extraction_identity"][field] = "previous extractor"
    metadata.write_text(json.dumps(stale))
    (first / "manifest.json").unlink()
    (first / "seal.json").unlink()
    seal(first)
    parse = code_index.ast.parse
    attempted = []

    def track(data, filename):
        attempted.append(filename)
        return parse(data, filename=filename)

    monkeypatch.setattr(code_index.ast, "parse", track)
    result = code_index.build_index(root, work / "second", first)
    assert result["status"] == "indexed" and result["counts"]["reused"] == 0
    assert attempted == ["stable.py"] and result["extraction_identity"] == identity


def test_partial_encoding_syntax_and_size_coverage(index_work):
    root, work = index_work
    put(root, "syntax.py", "def broken(:\n")
    put(root, "encoding.py", b"\xff\xfe\x00")
    put(root, "large.py", b"#" * 65)
    put(root, "latin.py", b"# coding: latin-1\nlabel = '\xe9'\nprint(label)\n")
    result = code_index.build_index(root, work / "index", max_file_bytes=64)
    assert result["status"] == "partial"
    assert result["counts"]["files"] == 4
    assert result["counts"]["parsed"] == 1
    assert result["counts"]["error"] == 2
    assert result["counts"]["oversize"] == 1
    rows = code_index.query_index(work / "index", "files")["rows"]
    assert all(row["sha256"] and row["error"] for row in rows if row["status"] != "parsed")
    assert "invalid syntax" in next(row for row in rows if row["path"] == "syntax.py")["error"]
    assert code_index.query_index(work / "index")["status"] == "partial"
    assert result["proof_claim"] is result["security_certification"] is False


def test_failed_files_are_not_reused_and_lower_bound_is_enforced(index_work, monkeypatch):
    root, work = index_work
    put(root, "bad.py", "def broken(:")
    put(root, "big.py", "long_function_name()\n")
    code_index.build_index(root, work / "first")
    original = code_index.ast.parse
    attempted = []

    def track(data, filename):
        attempted.append(filename)
        return original(data, filename=filename)

    monkeypatch.setattr(code_index.ast, "parse", track)
    result = code_index.build_index(root, work / "second", work / "first")
    assert attempted == ["bad.py"]
    assert result["counts"]["reused"] == 1
    smaller = code_index.build_index(root, work / "third", work / "first", max_file_bytes=4)
    assert smaller["counts"]["reused"] == 0 and smaller["counts"]["oversize"] == 2


@pytest.mark.parametrize("exception", [RecursionError, MemoryError])
def test_ast_resource_errors_discard_partial_facts(index_work, monkeypatch, exception):
    root, work = index_work
    put(root, "main.py", "first()\nsecond()\n")
    original = code_index._Facts.visit_Call
    calls = 0

    def fail(self, node):
        nonlocal calls
        calls += 1
        original(self, node)
        if calls == 2:
            raise exception

    monkeypatch.setattr(code_index._Facts, "visit_Call", fail)
    result = code_index.build_index(root, work / "index")
    assert result["status"] == "partial"
    assert result["counts"]["facts"] == 0
    assert code_index.query_index(work / "index", "files")["rows"][0]["error"] == exception.__name__


@pytest.mark.parametrize("exception", [RecursionError, MemoryError])
def test_parser_resource_errors_are_visible(index_work, monkeypatch, exception):
    root, work = index_work
    put(root, "main.py", "first()\n")

    def fail(*args, **kwargs):
        raise exception

    monkeypatch.setattr(code_index.ast, "parse", fail)
    result = code_index.build_index(root, work / "index")
    assert result["status"] == "partial" and result["counts"]["error"] == 1
    assert result["counts"]["facts"] == 0


def test_query_connection_is_readonly_without_extensions(index_work, monkeypatch):
    root, work = index_work
    put(root, "main.py", "first()\n")
    code_index.build_index(root, work / "index")
    connect = code_index.sqlite3.connect
    calls = []

    def track(database, **kwargs):
        calls.append((database, kwargs))
        return connect(database, **kwargs)

    monkeypatch.setattr(code_index.sqlite3, "connect", track)
    code_index.query_index(work / "index")
    assert len(calls) == 1
    database, options = calls[0]
    assert database.startswith("file:") and database.endswith("?mode=ro&immutable=1")
    assert options == {"uri": True}


def test_query_bounds_filters_and_immutable_output(index_work):
    root, work = index_work
    put(root, "many.py", "invoke()\n" * 1005)
    output = work / "index"
    code_index.build_index(root, output)
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    query = code_index.query_index(output, limit=100000)
    assert query["limit"] == code_index.QUERY_CAP
    assert len(query["rows"]) == 1000 and query["truncated"]
    assert len(code_index.query_index(output, name="invoke", limit=2)["rows"]) == 2
    assert len(code_index.query_index(output, name="many", limit=1)["rows"]) == 1
    assert not code_index.query_index(output, name="' OR 1=1 --")["rows"]
    assert code_index.query_index(output, "files", "many.py")["rows"][0]["path"] == "many.py"
    assert not code_index.query_index(output, "files", "missing.py")["rows"]
    assert before == {path.name: path.read_bytes() for path in output.iterdir()}
    for kwargs in [{"kind": "SELECT *"}, {"kind": []}, {"limit": 0},
                   {"limit": True}, {"limit": 1.5}, {"name": "a" * 513}]:
        with pytest.raises(EvidenceError):
            code_index.query_index(output, **kwargs)
    with pytest.raises(EvidenceError):
        code_index.build_index(root, output)


def test_artifact_tamper_and_previous_schema_rejected(index_work):
    root, work = index_work
    put(root, "main.py", "run()\n")
    first = work / "first"
    code_index.build_index(root, first)
    with sqlite3.connect(first / "code_index.sqlite3") as db:
        db.execute("DELETE FROM facts")
    for operation in [
        lambda: code_index.query_index(first),
        lambda: code_index.build_index(root, work / "second", first),
    ]:
        with pytest.raises(EvidenceError, match="hash mismatch"):
            operation()
    assert not (work / "second").exists()
    (first / "manifest.json").unlink()
    (first / "seal.json").unlink()
    with sqlite3.connect(first / "code_index.sqlite3") as db:
        db.execute("PRAGMA user_version=99")
    seal(first)
    with pytest.raises(EvidenceError, match="schema"):
        code_index.build_index(root, work / "third", first)


def test_outside_symlink_blocks_and_internal_directory_alias_is_canonical(index_work):
    root, work = index_work
    put(root, "pkg/real.py", "real()\n")
    (root / "alias").symlink_to("pkg", target_is_directory=True)
    result = code_index.build_index(root, work / "first")
    assert result["counts"]["files"] == 1
    outside = put(work, "outside.py", "outside()\n")
    (root / "external.py").symlink_to(outside)
    blocked = code_index.build_index(root, work / "second")
    assert blocked["status"] == "blocked"
    assert blocked["errors"] and blocked["counts"]["files"] == 0
    assert "outside source scope" in blocked["errors"][0]
    assert verify_seal(work / "second")
    assert code_index.query_index(work / "second")["rows"] == []


def test_source_drift_blocks_queries_and_retains_sealed_diagnostics(index_work, monkeypatch):
    root, work = index_work
    source = put(root, "main.py", "old()\n")
    original = code_index.ast.parse

    def mutate(data, filename):
        tree = original(data, filename=filename)
        source.write_text("new()\n")
        return tree

    monkeypatch.setattr(code_index.ast, "parse", mutate)
    result = code_index.build_index(root, work / "index")
    assert result["status"] == "blocked"
    assert result["before"] != result["after"]
    assert "drift" in result["errors"][0]
    assert code_index.query_index(work / "index")["rows"] == []
    assert verify_seal(work / "index")


def test_output_policy_and_disclosed_store(index_work):
    root, work = index_work
    put(root, "main.py", "run()\n")
    for output in [root, root / "new-index", work]:
        with pytest.raises(EvidenceError):
            code_index.build_index(root, output)
    (work / "linked").symlink_to(root, target_is_directory=True)
    with pytest.raises(EvidenceError, match="symlink"):
        code_index.build_index(root, work / "linked" / ".um-arts" / "index")
    result = code_index.build_index(root, root / ".um-arts" / "index")
    assert result["status"] == "indexed" and result["counts"]["files"] == 1
    second = code_index.build_index(
        root, root / ".um-arts" / "second", root / ".um-arts" / "index")
    assert second["status"] == "indexed" and second["counts"]["reused"] == 1


@pytest.mark.parametrize("bound", [0, -1, True, 2 * 1024 * 1024 + 1])
def test_invalid_file_bounds_rejected_before_writes(index_work, bound):
    root, work = index_work
    with pytest.raises(EvidenceError):
        code_index.build_index(root, work / "index", max_file_bytes=bound)
    assert not (work / "index").exists()


def test_parent_cli_arguments_and_statuses_match_api(index_work, capsys):
    from TOOLS.um_arts.__main__ import main

    root, work = index_work
    put(root, "main.py", "run()\n")
    output = work / "index"
    assert main(["code-index", "--root", str(root), "--output", str(output)]) == 0
    assert '"status": "indexed"' in capsys.readouterr().out
    assert main(["code-query", "--artifact", str(output), "--kind", "calls",
                 "--name", "run", "--limit", "1"]) == 0
    assert '"name": "run"' in capsys.readouterr().out
    put(root, "bad.py", "def broken(:\n")
    partial = work / "partial"
    assert main(["code-index", "--root", str(root), "--output", str(partial),
                 "--previous", str(output), "--max-file-bytes", "1024"]) == 2
    assert '"status": "partial"' in capsys.readouterr().out
    assert main(["code-query", "--artifact", str(partial), "--kind", "files"]) == 2
    text = capsys.readouterr().out
    assert '"status": "partial"' in text and "SyntaxError" in text


@pytest.mark.parametrize("damage", ["bad_bytes", "missing_table", "read_error"])
def test_sqlite_errors_are_evidence_errors_and_cli_blocked(index_work, capsys, damage):
    from TOOLS.um_arts.__main__ import main

    root, work = index_work
    put(root, "main.py", "run()\n")
    output = work / "index"
    code_index.build_index(root, output)
    database = output / "code_index.sqlite3"
    if damage == "bad_bytes":
        database.write_bytes(b"not a SQLite database")
    else:
        with sqlite3.connect(database) as db:
            db.execute("DROP TABLE facts")
            if damage == "read_error":
                db.execute("""
                    CREATE VIEW facts AS SELECT 'main.py' AS path, 'calls' AS kind,
                    'run' AS name, 1 AS line, 'main' AS qualified_symbol,
                    json_extract('invalid-json', '$') AS detail, 'unresolved' AS resolution
                """)
    (output / "manifest.json").unlink()
    (output / "seal.json").unlink()
    seal(output)
    with pytest.raises(EvidenceError, match="SQLite"):
        code_index.query_index(output)
    assert main(["code-query", "--artifact", str(output)]) == 2
    assert '"status": "blocked"' in capsys.readouterr().err
    with pytest.raises(EvidenceError, match="SQLite"):
        code_index.build_index(root, work / "second", output)


def test_sqlite_write_failure_is_evidence_error(index_work, monkeypatch):
    root, work = index_work

    def fail(*args, **kwargs):
        raise sqlite3.OperationalError("database unavailable")

    monkeypatch.setattr(code_index.sqlite3, "connect", fail)
    with pytest.raises(EvidenceError, match="database unavailable"):
        code_index.build_index(root, work / "index")
