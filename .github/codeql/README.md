# CodeQL slices

A single CodeQL database covering all of this repository's Python code is too
large for the analysis service. When that happens the analysis is skipped
outright, so "0 alerts" can mean "nothing was analysed". Python is therefore
analysed in **path slices**: one CodeQL job per slice, each with its own,
smaller database.

`slices.json` is the only list of slices. It drives three things:

| Command | Used by | What it does |
|---|---|---|
| `python TOOLS/checks/codeql_slices.py check` | CI (`codeql-language-matrix.yml`, first step) and `tests/test_codeql_slices.py` | Fails if any tracked `.py` file is in no slice, or if a slice path matches no tracked file (CodeQL aborts on a missing path) |
| `python TOOLS/checks/codeql_slices.py plan` | CI | Builds the job matrix: slices touching the changed files, or every slice on schedule/manual runs, or when the plan itself changes |
| `python TOOLS/checks/codeql_slices.py analyze SLICE...` | People and agents | Runs the same scoped analysis locally with the CodeQL CLI and writes SARIF plus a summary to `codeql-results/` |

`analyze` looks for the CLI in `--codeql`, then `$CODEQL_CLI`, then `PATH`,
then the GitHub runner tool cache. `--suite` is `security-extended` (the CI
default), `security-and-quality`, or `code-scanning`. `--fail-on-results`
makes it exit 1 on any error or warning result.

When adding a top-level directory or product with Python code, add it to a
slice. `check` fails until you do.

## Why this exists

Until this manifest was added, the slice list lived inside the workflow and was
maintained by hand. It had drifted: 666 of 4,006 tracked Python files were in
no slice and had never been analysed in CI. They included:

- all of EIGE (`12-AZ-IP/03-eige`);
- 20 other `12-AZ-IP` products;
- `hf-spaces`, `lodge`, `9-INFRASTRUCTURE` and the repository-root scripts.

The 5-GOVERNANCE slice also covered only `Unitary Pentad`.

## First full run (2026-10-06, CodeQL 2.27.1, `security-extended`)

Every Python slice was analysed locally: 4,007 files scanned out of 4,007 seen
(the root `conftest.py` is counted once per slice that sees it). The table
lists each result and what was done about it.

| Rule | Location | Disposition |
|---|---|---|
| `py/path-injection` (error) | `12-AZ-IP/18-um-reader/um_reader/app/server.py` | **Fixed.** `translate_path` fell back to the resolved path when it was outside both roots, so `GET /../../../etc/passwd` was served. Containment is now checked before any filesystem access, and anything else returns a 404. Regression test: `test_static_server_never_serves_paths_outside_ui_and_repo`. |
| `py/partial-ssrf` (error ×8) | `hf-spaces/axiom-journalist`, `terra-os`, `knowledge-hub`, `lean4-registry` | **Fixed.** User input was interpolated unencoded into URLs. Query values are now sent with `params=`, coordinates are validated as numbers in range, and file paths are restricted to repository-relative paths (no `..`, `.`, empty segments, scheme, query or fragment) and percent-encoded. |
| `py/stack-trace-exposure` (error) | `12-AZ-IP/01-axiom-os/api/server.py` | **Fixed.** `/health/vram` returned the exception text. It now logs the exception and returns a fixed message. `/health/deep`, which had the same pattern but was not flagged, now returns only the exception type. |
| `py/stack-trace-exposure` (error) | `lodge/server.py` via `lodge/rag_bridge.py` | **Fixed.** Exception text from the RAG index reached `/exchange/ask`. It is now logged, and callers get a fixed message. |
| `py/overly-permissive-file` (warning) | `12-AZ-IP/03-eige/src/sentinel_load_balance.py` | **Fixed.** Override dossiers were created `0o644`; they are now `0o600`. |
| `py/xml-bomb` (warning) | `12-AZ-IP/10-filmers-companion/.../service.py` | **Mitigated; still reported.** FDX never needs a DTD, so payloads with `<!DOCTYPE` or `<!ENTITY` are rejected before parsing (test: `test_import_script_fdx_rejects_entity_declarations`). The Python 3.12 expat parser also limits entity amplification. CodeQL does not model the string guard. |
| `py/polynomial-redos` (warning ×3) | `12-AZ-IP/10-filmers-companion/.../service.py` | **Not exploitable.** Each pattern is matched against one stripped script line with no line breaks. |
| `py/polynomial-redos` (warning) | `ox_navigator/engine/merlin_runtime.py` (`_EMAIL_RE`) | **Not exploitable.** The negative lookbehind prevents suffix retries. `tests/test_merlin_v1.py` already pins behaviour on 100,000-character adversarial inputs. |
| `py/http-response-splitting`, `py/cookie-injection` | `ox_navigator/app/server.py` | **False positive.** The echoed `Origin` must be on an allowlist, and header values parsed by `http.server` cannot contain CR/LF. Session cookies are built only from a 32-hex-digit id that `_sign_session_id` enforces. |
| `py/path-injection` | `ox_navigator/engine/merlin_local_execution.py` | **False positive.** `_resolve_cwd` calls `Path.relative_to(REPO_ROOT)`, which raises for any path outside the repository. CodeQL does not model that call as a guard. |
| `py/incomplete-url-substring-sanitization` (warning ×9) | test files only | **Not applicable.** These are assertions on URLs produced by the code under test, not sanitisers. |

After the fixes, every slice except `python-runtime-integration` has no
error-level results. That slice still reports the PsiCat false positives
described above. The remaining warnings are the ones marked above as mitigated,
not exploitable, false positive, or not applicable.

The EIGE slice was also run with `security-and-quality` (172 queries). The
dispositions of those results are in `12-AZ-IP/03-eige/CHANGELOG.md`.

A CodeQL run with no results is evidence that its queries found nothing. It is
not a security certification.
