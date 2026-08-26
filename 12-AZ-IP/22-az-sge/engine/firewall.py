# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/firewall.py — Packet-Filter Policy Engine
=================================================

A pure-Python packet-filter policy engine that:

  1. Accepts structured firewall rules (allow/deny + priority)
  2. Evaluates any NetworkEvent or raw 5-tuple against the ordered rule set
  3. Provides a default-deny-all policy (true "default drop")
  4. Supports stateful connection tracking (SYN-allowed sessions persist)
  5. Rate-limiting (token-bucket per source IP)
  6. Geo-block (CIDR-based; ships with known high-risk CIDRs as defaults)
  7. Rule compiler: converts JSON rule definitions to PolicyRule objects
  8. Audit log: every decision is recorded with the matching rule name

In production this engine would be wired to nftables / iptables / eBPF via
a kernel bridge.  In the current implementation it is a user-space policy
simulator — the same logic that would be JIT-compiled into eBPF bytecode.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import ipaddress
import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .intrusion_detector import NetworkEvent, Protocol


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Action(str, Enum):
    ALLOW   = "allow"
    DENY    = "deny"
    LOG     = "log"     # allow but record
    RATE    = "rate"    # allow if within rate limit, else deny


class Direction(str, Enum):
    INBOUND  = "inbound"
    OUTBOUND = "outbound"
    ANY      = "any"


# ---------------------------------------------------------------------------
# PolicyRule
# ---------------------------------------------------------------------------

@dataclass
class PolicyRule:
    """A single firewall policy rule.

    Priority: lower number = higher priority (evaluated first).
    """
    name: str
    priority: int
    action: Action
    direction: Direction = Direction.ANY

    # Match criteria (None = wildcard)
    src_ip: Optional[str] = None     # CIDR or exact IP
    dst_ip: Optional[str] = None     # CIDR or exact IP
    src_port: Optional[int] = None   # exact port or None
    dst_port: Optional[int] = None   # exact port or None
    protocol: Optional[Protocol] = None

    # Rate limit (tokens per second) — only used when action = RATE
    rate_limit_tps: float = 10.0

    # Human-readable description
    description: str = ""

    def _ip_matches(self, rule_cidr: Optional[str], event_ip: str) -> bool:
        if rule_cidr is None:
            return True
        try:
            network = ipaddress.ip_network(rule_cidr, strict=False)
            return ipaddress.ip_address(event_ip) in network
        except ValueError:
            return event_ip == rule_cidr

    def matches(self, event: NetworkEvent, direction: Direction = Direction.INBOUND) -> bool:
        """Return True if this rule matches the event."""
        if self.direction not in (direction, Direction.ANY):
            return False
        if not self._ip_matches(self.src_ip, event.src_ip):
            return False
        if not self._ip_matches(self.dst_ip, event.dst_ip):
            return False
        if self.src_port is not None and self.src_port != event.src_port:
            return False
        if self.dst_port is not None and self.dst_port != event.dst_port:
            return False
        if self.protocol is not None and self.protocol != event.protocol:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "priority": self.priority,
            "action": self.action.value,
            "direction": self.direction.value,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol.value if self.protocol else None,
            "description": self.description,
        }


# ---------------------------------------------------------------------------
# Built-in default rules
# ---------------------------------------------------------------------------

BUILTIN_RULES: List[PolicyRule] = [
    # Allow established/related (stateful — handled by connection tracker)
    PolicyRule(
        name="ALLOW_LOOPBACK",
        priority=1,
        action=Action.ALLOW,
        src_ip="127.0.0.0/8",
        description="Allow all loopback traffic",
    ),
    PolicyRule(
        name="ALLOW_LAN_RFC1918",
        priority=2,
        action=Action.ALLOW,
        src_ip="10.0.0.0/8",
        description="Allow RFC-1918 private 10.x LAN",
    ),
    PolicyRule(
        name="ALLOW_LAN_RFC1918_172",
        priority=3,
        action=Action.ALLOW,
        src_ip="172.16.0.0/12",
        description="Allow RFC-1918 private 172.16–31.x LAN",
    ),
    PolicyRule(
        name="ALLOW_LAN_RFC1918_192",
        priority=4,
        action=Action.ALLOW,
        src_ip="192.168.0.0/16",
        description="Allow RFC-1918 private 192.168.x.x LAN",
    ),
    # Block known malicious CIDRs
    PolicyRule(
        name="DENY_TOR_EXIT_CIDR",
        priority=10,
        action=Action.DENY,
        src_ip="185.220.101.0/24",
        description="Deny known Tor exit node CIDR",
    ),
    PolicyRule(
        name="DENY_BOGON_0_8",
        priority=11,
        action=Action.DENY,
        src_ip="0.0.0.0/8",
        description="Deny IANA unallocated 0.x",
    ),
    PolicyRule(
        name="DENY_BOGON_240_4",
        priority=12,
        action=Action.DENY,
        src_ip="240.0.0.0/4",
        description="Deny IANA reserved 240.x",
    ),
    # Allow essential outbound services
    PolicyRule(
        name="ALLOW_DNS_OUT",
        priority=20,
        action=Action.ALLOW,
        direction=Direction.OUTBOUND,
        dst_port=53,
        description="Allow outbound DNS",
    ),
    PolicyRule(
        name="ALLOW_HTTPS_OUT",
        priority=21,
        action=Action.ALLOW,
        direction=Direction.OUTBOUND,
        dst_port=443,
        description="Allow outbound HTTPS",
    ),
    PolicyRule(
        name="ALLOW_HTTP_OUT",
        priority=22,
        action=Action.LOG,
        direction=Direction.OUTBOUND,
        dst_port=80,
        description="Log outbound HTTP (unencrypted — audit trail)",
    ),
    # Rate-limit SSH inbound
    PolicyRule(
        name="RATE_SSH_INBOUND",
        priority=30,
        action=Action.RATE,
        direction=Direction.INBOUND,
        dst_port=22,
        rate_limit_tps=2.0,
        description="Rate-limit inbound SSH to 2 connections/second",
    ),
    # Block raw SMB from internet
    PolicyRule(
        name="DENY_SMB_INBOUND_EXTERNAL",
        priority=40,
        action=Action.DENY,
        direction=Direction.INBOUND,
        dst_port=445,
        description="Block SMB/445 from non-LAN sources",
    ),
    PolicyRule(
        name="DENY_RDP_INBOUND",
        priority=41,
        action=Action.DENY,
        direction=Direction.INBOUND,
        dst_port=3389,
        description="Block RDP from internet (VPN-only access)",
    ),
    # Default deny at lowest priority
    PolicyRule(
        name="DEFAULT_DENY_ALL",
        priority=9999,
        action=Action.DENY,
        description="Default deny — no prior rule matched",
    ),
]


# ---------------------------------------------------------------------------
# Audit log entry
# ---------------------------------------------------------------------------

@dataclass
class FirewallDecision:
    timestamp: float
    action: Action
    rule_name: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    direction: str

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action.value,
            "rule_name": self.rule_name,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "direction": self.direction,
        }


# ---------------------------------------------------------------------------
# Token bucket rate limiter
# ---------------------------------------------------------------------------

class TokenBucket:
    """Per-source token-bucket rate limiter."""

    def __init__(self, rate_tps: float, burst: float = 5.0) -> None:
        self._rate = rate_tps
        self._burst = burst
        self._tokens: float = burst
        self._last: Optional[float] = None

    def consume(self, ts: Optional[float] = None) -> bool:
        """Attempt to consume one token.  Returns True if allowed."""
        now = ts if ts is not None else time.time()
        if self._last is not None:
            elapsed = now - self._last
            self._tokens = min(self._burst, self._tokens + elapsed * self._rate)
        self._last = now
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            return True
        return False


# ---------------------------------------------------------------------------
# Connection tracker (stateful)
# ---------------------------------------------------------------------------

class ConnectionTracker:
    """Tracks TCP connections to permit return traffic."""

    def __init__(self, ttl_seconds: float = 300.0) -> None:
        self._ttl = ttl_seconds
        # key: (src_ip, dst_ip, src_port, dst_port) → expiry timestamp
        self._table: Dict[Tuple, float] = {}

    def register(self, event: NetworkEvent) -> None:
        """Register an allowed outbound connection for stateful return."""
        key = (event.src_ip, event.dst_ip, event.src_port, event.dst_port)
        self._table[key] = event.timestamp + self._ttl

    def is_established(self, event: NetworkEvent) -> bool:
        """Check if the event is part of an already-established session."""
        now = event.timestamp
        self._prune(now)
        # Check both directions of the tuple
        key_fwd = (event.dst_ip, event.src_ip, event.dst_port, event.src_port)
        return key_fwd in self._table and self._table[key_fwd] > now

    def _prune(self, now: float) -> None:
        expired = [k for k, exp in self._table.items() if exp <= now]
        for k in expired:
            del self._table[k]


# ---------------------------------------------------------------------------
# PolicyEngine — main firewall
# ---------------------------------------------------------------------------

class PolicyEngine:
    """User-space packet-filter policy engine.

    Parameters
    ----------
    rules : list of PolicyRule, optional
        Overrides the built-in default rule set.  If omitted, BUILTIN_RULES
        are used.
    max_audit_log : int
        Maximum number of decision records to retain in memory.
    """

    def __init__(
        self,
        rules: Optional[List[PolicyRule]] = None,
        max_audit_log: int = 10_000,
    ) -> None:
        self._rules: List[PolicyRule] = sorted(
            rules if rules is not None else list(BUILTIN_RULES),
            key=lambda r: r.priority,
        )
        self._conn_tracker = ConnectionTracker()
        self._rate_limiters: Dict[Tuple[str, str], TokenBucket] = {}
        self._audit: deque = deque(maxlen=max_audit_log)

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, rule: PolicyRule) -> None:
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority)

    def remove_rule(self, name: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.name != name]
        return len(self._rules) < before

    def list_rules(self) -> List[dict]:
        return [r.to_dict() for r in self._rules]

    # ------------------------------------------------------------------
    # Decision
    # ------------------------------------------------------------------

    def evaluate(
        self,
        event: NetworkEvent,
        direction: Direction = Direction.INBOUND,
    ) -> FirewallDecision:
        """Evaluate one NetworkEvent against the policy.

        Returns a FirewallDecision (ALLOW, DENY, or LOG).
        """
        # Stateful: permit established return traffic
        if self._conn_tracker.is_established(event):
            dec = FirewallDecision(
                timestamp=event.timestamp,
                action=Action.ALLOW,
                rule_name="STATEFUL_ESTABLISHED",
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
                src_port=event.src_port,
                dst_port=event.dst_port,
                protocol=event.protocol.value,
                direction=direction.value,
            )
            self._audit.append(dec)
            return dec

        for rule in self._rules:
            if not rule.matches(event, direction):
                continue

            action = rule.action
            if action == Action.RATE:
                bucket_key = (event.src_ip, rule.name)
                if bucket_key not in self._rate_limiters:
                    self._rate_limiters[bucket_key] = TokenBucket(rule.rate_limit_tps)
                allowed = self._rate_limiters[bucket_key].consume(event.timestamp)
                action = Action.ALLOW if allowed else Action.DENY

            if action in (Action.ALLOW, Action.LOG):
                if direction == Direction.OUTBOUND:
                    self._conn_tracker.register(event)

            dec = FirewallDecision(
                timestamp=event.timestamp,
                action=action,
                rule_name=rule.name,
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
                src_port=event.src_port,
                dst_port=event.dst_port,
                protocol=event.protocol.value,
                direction=direction.value,
            )
            self._audit.append(dec)
            return dec

        # Fallback (should not reach here if DEFAULT_DENY_ALL is present)
        dec = FirewallDecision(
            timestamp=event.timestamp,
            action=Action.DENY,
            rule_name="IMPLICIT_DENY",
            src_ip=event.src_ip,
            dst_ip=event.dst_ip,
            src_port=event.src_port,
            dst_port=event.dst_port,
            protocol=event.protocol.value,
            direction=direction.value,
        )
        self._audit.append(dec)
        return dec

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_log(self) -> List[dict]:
        return [d.to_dict() for d in self._audit]

    def audit_summary(self) -> dict:
        denied = sum(1 for d in self._audit if d.action == Action.DENY)
        allowed = sum(1 for d in self._audit if d.action in (Action.ALLOW, Action.LOG))
        return {
            "total": len(self._audit),
            "allowed": allowed,
            "denied": denied,
        }


# ---------------------------------------------------------------------------
# Rule compiler: JSON → PolicyRule list
# ---------------------------------------------------------------------------

def compile_rules_from_json(json_str: str) -> List[PolicyRule]:
    """Parse a JSON rule definition and return PolicyRule objects.

    JSON format::

        [
          {
            "name": "BLOCK_TELNET",
            "priority": 50,
            "action": "deny",
            "direction": "inbound",
            "dst_port": 23,
            "description": "Block Telnet"
          },
          ...
        ]
    """
    raw = json.loads(json_str)
    rules = []
    for entry in raw:
        proto_str = entry.get("protocol")
        try:
            proto = Protocol(proto_str) if proto_str else None
        except ValueError:
            proto = None
        try:
            direction = Direction(entry.get("direction", "any"))
        except ValueError:
            direction = Direction.ANY
        rules.append(PolicyRule(
            name=entry["name"],
            priority=int(entry.get("priority", 100)),
            action=Action(entry.get("action", "deny")),
            direction=direction,
            src_ip=entry.get("src_ip"),
            dst_ip=entry.get("dst_ip"),
            src_port=entry.get("src_port"),
            dst_port=entry.get("dst_port"),
            protocol=proto,
            rate_limit_tps=float(entry.get("rate_limit_tps", 10.0)),
            description=entry.get("description", ""),
        ))
    return rules
