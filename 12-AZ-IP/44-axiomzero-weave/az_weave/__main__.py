# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Explicit local-operator CLI; query/capabilities have no persistent effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .api import Weave, capabilities, run_readonly
from .server import make_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AxiomZero Weave / Product 44")
    parser.add_argument("--repo-root", type=Path, help="Checkout root (required for a non-editable installed wheel)")
    parser.add_argument("--state-dir", type=Path, default=Path(".axiomzero-weave"))
    parser.add_argument("--checkpoint", action="append", default=[], metavar="ID=PATH")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")
    query = sub.add_parser("query")
    query.add_argument("query")
    query.add_argument("--limit", type=int, default=5)
    study = sub.add_parser("investigate")
    study.add_argument("query")
    study.add_argument("--experiment", required=True, help="Exact experiment JSON object")
    study.add_argument("--oracle", required=True, help="Explicit Oracle JSON object")
    study.add_argument("--decision-id")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8144)
    for name in ("approve", "invoke"):
        action = sub.add_parser(name)
        action.add_argument("action")
        action.add_argument("--arguments", required=True, help="Exact JSON object")
        if name == "approve":
            action.add_argument("--obligations", required=True, help="Five explicit PASS/FAIL/UNKNOWN verdicts")
            action.add_argument("--sources", default="[]", help="Source records from a query receipt")
            action.add_argument("--ttl", type=int, default=300)
        else:
            action.add_argument("--decision-id")
    for name in ("decision", "revoke", "reconcile"):
        decision = sub.add_parser(name)
        decision.add_argument("decision_id")
        if name == "reconcile":
            decision.add_argument("resolution", choices=["CONFIRMED_EFFECT", "CONFIRMED_NO_EFFECT"])
    args = parser.parse_args(argv)
    try:
        checkpoints = {}
        for entry in args.checkpoint:
            identifier, value = entry.split("=", 1)
            if not identifier or not value:
                raise ValueError("checkpoint must be a nonempty ID=PATH")
            if identifier in checkpoints:
                raise ValueError("duplicate checkpoint identifier")
            checkpoints[identifier] = Path(value)
        if args.command == "query":
            result = run_readonly(args.query, args.limit, repo_root=args.repo_root)
        elif args.command == "capabilities":
            result = capabilities(repo_root=args.repo_root, state_dir=args.state_dir,
                                  checkpoints=checkpoints)
        else:
            weave = Weave(args.state_dir, repo_root=args.repo_root, checkpoints=checkpoints)
            principal = "local-operator"
            if args.command == "serve":
                with make_server(weave, port=args.port) as server:
                    print(f"Product 44: http://127.0.0.1:{server.server_port}\n"
                          f"Operator token file: {args.state_dir / 'operator.token'}", flush=True)
                    server.serve_forever()
                return 0
            if args.command == "approve":
                result = {"decision_id": weave.approve(
                    args.action, json.loads(args.arguments), principal,
                    obligations=json.loads(args.obligations), sources=json.loads(args.sources), ttl=args.ttl)}
            elif args.command == "investigate":
                result = weave.investigate(args.query, principal, experiment=json.loads(args.experiment),
                                           oracle=json.loads(args.oracle), decision_id=args.decision_id)
            elif args.command == "invoke":
                result = weave.invoke(args.action, json.loads(args.arguments), principal, args.decision_id)
            elif args.command == "decision":
                result = weave.journal.get(args.decision_id, principal)
            elif args.command == "revoke":
                weave.journal.revoke(args.decision_id, principal)
                result = {"state": "REVOKED"}
            else:
                weave.journal.reconcile(args.decision_id, principal, resolution=args.resolution)
                result = {"state": args.resolution}
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, ImportError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
