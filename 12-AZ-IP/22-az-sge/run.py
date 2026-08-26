#!/usr/bin/env python3
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
run.py — AxiomZero System Security Governance Engine launcher
=============================================================

Usage
-----
  python run.py                        # start dashboard on 127.0.0.1:7622
  python run.py --port 8000            # alternate port
  python run.py --demo                 # generate demo threats + serve
  python run.py --scan /path/to/dir   # scan directory, print JSON report
  python run.py --check-domain example.com
  python run.py --check-hash 44d88612fea8a8f36de82e1278abb02f
  python run.py --check-cve CVE-2024-21762
  python run.py --audit-deps /path/to/project
  python run.py --status               # print engine status JSON

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.sge_core import SGECore, SGEConfig
from engine.intrusion_detector import NetworkEvent, Protocol, ProcessEvent
from engine.surveillance_guard import PrivacyAlert
from app.server import serve_ui


# ---------------------------------------------------------------------------
# Demo event injection
# ---------------------------------------------------------------------------

def run_demo(sge: SGECore) -> None:
    """Inject a variety of demo events to populate the dashboard."""
    print("[SGE demo] Injecting demo events...")

    # SQL injection attempt
    net_evt = NetworkEvent(
        src_ip="203.0.113.42",
        dst_ip="10.0.0.1",
        src_port=54321,
        dst_port=80,
        protocol=Protocol.HTTP,
        payload_size=512,
        http_method="POST",
        http_path="/login?id=1'+OR+1=1--",
        payload_snippet=b"username=admin&password=' OR 1=1--",
    )
    alerts, decision = sge.inspect_network(net_evt)
    print(f"  SQL injection: {len(alerts)} alert(s), firewall={decision.action.value}")

    # Port scan
    for port in [22, 23, 80, 443, 445, 3389, 5432, 6379, 8080, 27017, 3306, 1433, 135, 139, 25, 21]:
        ev = NetworkEvent(
            src_ip="198.51.100.1",
            dst_ip="10.0.0.1",
            src_port=40000 + port,
            dst_port=port,
            protocol=Protocol.TCP,
            payload_size=0,
            flags="SYN",
        )
        sge.inspect_network(ev)
    print("  Port scan events injected")

    # Malware scan (EICAR test)
    eicar = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    scan, qr = sge.scan_file.__func__(sge, "/tmp/eicar_test.com") if False else (
        sge._malware.scan_bytes(eicar, "eicar_test.com"),
        None,
    )
    if scan.threat_score > 0:
        qr = sge._quarantine.handle_file_scan(scan, eicar)
        sge._emit_event("file_scan", scan.risk_level, scan.threat_score,
                        f"File scan: eicar_test.com", str(scan.to_dict())[:256], "eicar_test.com")
    print(f"  EICAR scan: score={scan.threat_score:.0f} risk={scan.risk_level}")

    # Suspicious process
    proc = ProcessEvent(
        pid=31337,
        name="powershell.exe",
        cmdline="powershell.exe -EncodedCommand dABoAGkAcwBfAGkAcwBfAG0AYQBsAHcAYQByAGUA",
        parent_pid=1234,
        parent_name="winword.exe",
        user="victim",
    )
    p_alerts = sge.inspect_process(proc)
    print(f"  Malicious process: {len(p_alerts)} alert(s)")

    # Privacy audit
    fake_page = b"""
    <script src="https://fpjs.io/v3/bsX"></script>
    <script>eval(unescape('%61%6c%65%72%74'))</script>
    <iframe width=0 height=0 src="http://evil.example.com/exploit"></iframe>
    """
    priv_alerts = sge.full_privacy_audit(page_content=fake_page)
    print(f"  Privacy audit: {len(priv_alerts)} alert(s)")

    # Refresh threat intel (offline fallback)
    n = sge.refresh_threat_intel()
    print(f"  Threat intel: {n} indicators loaded")

    print("[SGE demo] Done. Dashboard ready.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="AxiomZero System Security Governance Engine",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("--host", default="127.0.0.1", help="Dashboard bind host (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=7622, help="Dashboard port (default: 7622)")
    p.add_argument("--no-serve", action="store_true", help="Do not start HTTP dashboard")
    p.add_argument("--demo", action="store_true", help="Inject demo events before serving")
    p.add_argument("--scan", metavar="PATH", help="Scan a file or directory for malware")
    p.add_argument("--check-domain", metavar="DOMAIN", help="Check a domain against tracker/C2 lists")
    p.add_argument("--check-hash", metavar="HASH", help="Check a file hash for known malware")
    p.add_argument("--check-cve", metavar="CVE_ID", help="Look up a CVE in threat intel")
    p.add_argument("--audit-deps", metavar="PATH", help="Audit dependency manifests in PATH")
    p.add_argument("--status", action="store_true", help="Print engine status JSON and exit")
    p.add_argument("--nvd-key", default="", help="NVD API key for CVE feed")
    p.add_argument("--quarantine-dir", default="", help="Quarantine vault directory")
    return p


def main() -> None:
    args = build_parser().parse_args()

    cfg = SGEConfig(
        nvd_api_key=args.nvd_key or None,
        quarantine_dir=args.quarantine_dir or None,
    )
    sge = SGECore(cfg)
    print(f"[SGE] AxiomZero Security Governance Engine v{sge.ENGINE_VERSION} started")

    # One-shot commands
    if args.status:
        print(json.dumps(sge.status(), indent=2))
        return

    if args.scan:
        p = Path(args.scan)
        if p.is_file():
            scan, qr = sge.scan_file(p)
            print(json.dumps(scan.to_dict(), indent=2))
        else:
            results = sge.scan_directory(p)
            flagged = [r for r in results if r.threat_score > 0]
            print(f"Scanned {len(results)} files, {len(flagged)} flagged:")
            for r in flagged:
                print(f"  {r.risk_level:8s} score={r.threat_score:.0f}  {r.path}")
        return

    if args.check_domain:
        blocked, rule = sge.check_domain(args.check_domain)
        print(json.dumps({"domain": args.check_domain, "blocked": blocked, "matched_rule": rule}, indent=2))
        return

    if args.check_hash:
        ind = sge.lookup_file_hash(args.check_hash)
        print(json.dumps({"hash": args.check_hash, "is_malware": ind is not None,
                          "indicator": ind.to_dict() if ind else None}, indent=2))
        return

    if args.check_cve:
        ind = sge.lookup_cve(args.check_cve)
        print(json.dumps({"cve_id": args.check_cve, "found": ind is not None,
                          "indicator": ind.to_dict() if ind else None}, indent=2))
        return

    if args.audit_deps:
        report = sge.dependency_report(args.audit_deps)
        print(json.dumps(report.to_dict(), indent=2))
        return

    # Dashboard mode
    if args.demo:
        run_demo(sge)

    if not args.no_serve:
        server = serve_ui(sge, host=args.host, port=args.port, daemon=False)
        print(f"[SGE] Dashboard → http://{args.host}:{args.port}/")
        print("[SGE] Press Ctrl-C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[SGE] Shutdown.")
    else:
        print(json.dumps(sge.status(), indent=2))


if __name__ == "__main__":
    main()
