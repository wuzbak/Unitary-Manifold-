# PsiCat External Intake

This is the quarantine and triage area for files or test reports sent by PsiCat
operating outside this repository. An external report may be useful evidence,
but its failures are **not failures of the repository's canonical test suite**
unless the affected code and tests have been reviewed and integrated.

## Intake and triage

For each submission, create a dated folder under `submissions/` using
`YYYY-MM-DD-source-short-description/`. Preserve the received files there
without executing or silently modifying them. Add an `INTAKE.md` that records:

- receipt date and authorized source/provenance
- file inventory and any sanitization or conversion
- reported command, environment, revision, expected result, and observed result
- triage status: `pending`, `accepted`, `rejected`, or `incomplete`
- reviewer decision and, if accepted, the destination for separately reviewed work

Treat external files as untrusted input. Do not commit credentials, secrets,
private user data, or unrelated proprietary material. Do not run submitted code
in the repository environment. If a submission cannot safely be retained,
record a sanitized description and why the original was excluded.

## Test-pipeline boundary

Files in this intake area are evidence only. Do not add unreviewed external
tests to `tests/`, a product's test directory, or another canonical test suite.
The intake area is excluded from pytest discovery, while CI continues to run its
explicitly configured suites. A submission becomes a project test only after
review, relocation to the appropriate test suite, and verification by the
normal project test pipeline.

Keep external failures and their provenance here when useful; do not change
canonical test results or status counts to make an external report appear to
be part of the repository's regression record.

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
