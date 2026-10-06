# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Public Trust Report: exactly what was verified, what failed, and what was not checked.

The report never summarises to a single "integrity score".  Each check is
listed individually with one of four statuses, and the fixed list of things
EIGE cannot establish is always printed.  Three plain-language templates are
provided: election officials, courts, and voters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

VERIFIED = "verified"
FAILED = "failed"
NOT_CHECKED = "not_checked"
WARNING = "warning"
STATUSES = (VERIFIED, FAILED, WARNING, NOT_CHECKED)

OUT_OF_SCOPE = (
    "EIGE does not count votes and does not replace certified voting systems or paper ballots.",
    "EIGE cannot detect anything that happened to a ballot before it was scanned and logged "
    "(for example, altered or substituted paper, or a scanner that misreads marks); only an "
    "audit of the paper ballots can check that.",
    "EIGE is not end-to-end verifiable voting: voters cannot use it to confirm their own ballot "
    "was counted as cast.",
    "Signatures show which key signed a record, not that the person holding the key acted honestly.",
    "Statistical screens produce investigation leads, not evidence of fraud.",
)


@dataclass(frozen=True)
class CheckResult:
    check: str
    status: str
    detail: str

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"unknown status {self.status!r}")

    def as_dict(self) -> dict:
        return {"check": self.check, "status": self.status, "detail": self.detail}


@dataclass
class VerificationReport:
    subject: str
    checks: List[CheckResult] = field(default_factory=list)

    def add(self, check: str, status: str, detail: str) -> None:
        self.checks.append(CheckResult(check, status, detail))

    def by_status(self, status: str) -> List[CheckResult]:
        return [c for c in self.checks if c.status == status]

    @property
    def passed(self) -> bool:
        return not self.by_status(FAILED)

    def counts(self) -> Dict[str, int]:
        return {s: len(self.by_status(s)) for s in STATUSES}

    def as_dict(self) -> dict:
        return {
            "format": "eige.verification_report.v1",
            "subject": self.subject,
            "passed": self.passed,
            "counts": self.counts(),
            "checks": [c.as_dict() for c in self.checks],
            "out_of_scope": list(OUT_OF_SCOPE),
        }

    def render(self, audience: str = "official") -> str:
        if audience not in TEMPLATES:
            raise ValueError(f"audience must be one of {sorted(TEMPLATES)}")
        return TEMPLATES[audience](self)


def _section(title: str, items: List[CheckResult]) -> List[str]:
    if not items:
        return []
    return [title] + [f"  - {c.check}: {c.detail}" for c in items] + [""]


def _official(r: VerificationReport) -> str:
    c = r.counts()
    lines = [
        f"EIGE verification report — {r.subject}",
        f"Result: {'no failed checks' if r.passed else str(c[FAILED]) + ' FAILED check(s) — resolve before certification'}",
        f"Verified {c[VERIFIED]} · Failed {c[FAILED]} · Warnings {c[WARNING]} · Not checked {c[NOT_CHECKED]}",
        "",
    ]
    lines += _section("FAILED (must be resolved or formally explained):", r.by_status(FAILED))
    lines += _section("WARNINGS (document in the canvass record):", r.by_status(WARNING))
    lines += _section("VERIFIED:", r.by_status(VERIFIED))
    lines += _section("NOT CHECKED (no data supplied — this is not a pass):", r.by_status(NOT_CHECKED))
    lines += ["Limits of this report:"] + [f"  - {x}" for x in OUT_OF_SCOPE]
    return "\n".join(lines)


def _court(r: VerificationReport) -> str:
    lines = [
        f"Statement of verification results — {r.subject}",
        "",
        "1. Method. Each check below was performed by recomputation from published artifacts using "
        + "the open-source EIGE verifier. Any party can repeat it and should obtain identical results.",
        "2. Results by check:",
    ]
    for i, c in enumerate(r.checks, start=1):
        lines.append(f"   2.{i} {c.check} — {c.status.upper().replace('_', ' ')}. {c.detail}")
    lines += [
        "3. A status of NOT CHECKED means no conclusion is drawn in either direction.",
        "4. Limitations:",
    ] + [f"   - {x}" for x in OUT_OF_SCOPE]
    return "\n".join(lines)


def _voter(r: VerificationReport) -> str:
    c = r.counts()
    if not r.passed:
        headline = (f"{c[FAILED]} check(s) did not pass. That does not by itself mean the result is wrong — "
                    "it means election officials must explain or correct something before certifying.")
    elif c[NOT_CHECKED]:
        headline = (f"Every check that could be run passed, but {c[NOT_CHECKED]} check(s) could not be run "
                    "because the needed records were not published.")
    else:
        headline = "Every published check passed."
    lines = [f"What was checked about {r.subject}", "", headline, ""]
    for x in r.checks:
        mark = {"verified": "✓", "failed": "✗", "warning": "!", "not_checked": "–"}[x.status]
        lines.append(f"{mark} {x.check}")
    lines += ["", "What these checks cannot tell you:"] + [f"• {x}" for x in OUT_OF_SCOPE]
    return "\n".join(lines)


TEMPLATES = {"official": _official, "court": _court, "voter": _voter}
