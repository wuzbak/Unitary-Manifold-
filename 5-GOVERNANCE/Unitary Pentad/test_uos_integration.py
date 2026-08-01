# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Integration tests for the UOS Phase 3 networking, shell, and profiler stack."""

from __future__ import annotations

import os
import sys
import time

import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from UOS.constants import BRAIDED_SOUND_SPEED, WINDING_NUMBER
from UOS.network import NetworkTopology, PentadNetworkNode
from UOS.profiler import EntropyProfiler, SENTINEL_CAPACITY, SentinelProfiler
from UOS.shell import CommandParser, PentadShell


@pytest.fixture()
def node_pair():
    a = PentadNetworkNode("alpha", "127.0.0.1", 9001)
    b = PentadNetworkNode("beta", "127.0.0.1", 9002)
    a.connect(b)
    return a, b


class TestPentadNetworkNode:
    def test_connect_records_peers(self, node_pair):
        a, b = node_pair
        assert a.get_connected_nodes() == ["beta"]
        assert b.get_connected_nodes() == ["alpha"]

    def test_connect_self_returns_false(self):
        node = PentadNetworkNode("solo", "127.0.0.1", 9000)
        assert node.connect(node) is False

    def test_broadcast_returns_peer_count(self, node_pair):
        a, _ = node_pair
        assert a.broadcast("hello") == 1

    def test_broadcast_appends_log(self, node_pair):
        a, _ = node_pair
        a.broadcast("sync")
        assert len(a._broadcast_log) == 1

    def test_remote_receives_broadcast_log(self, node_pair):
        a, b = node_pair
        a.broadcast("sync")
        assert b._broadcast_log[-1]["message"] == "sync"

    def test_entropy_zero_before_broadcast(self, node_pair):
        a, _ = node_pair
        assert a.get_network_entropy() == 0.0

    def test_entropy_bounded_after_broadcasts(self):
        a = PentadNetworkNode("a", "127.0.0.1", 9100)
        b = PentadNetworkNode("b", "127.0.0.1", 9101)
        c = PentadNetworkNode("c", "127.0.0.1", 9102)
        a.connect(b)
        a.connect(c)
        a.broadcast("one")
        a.broadcast("two")
        assert 0.0 <= a.get_network_entropy() <= 1.0

    def test_multiple_connections_sorted(self):
        a = PentadNetworkNode("a", "127.0.0.1", 9100)
        b = PentadNetworkNode("b", "127.0.0.1", 9101)
        c = PentadNetworkNode("c", "127.0.0.1", 9102)
        a.connect(c)
        a.connect(b)
        assert a.get_connected_nodes() == ["b", "c"]

    @pytest.mark.parametrize("message", ["status", "alert", "phase-lock", "diagnostic"])
    def test_broadcast_accepts_varied_messages(self, node_pair, message):
        a, _ = node_pair
        assert a.broadcast(message) == 1

    @pytest.mark.parametrize("count", [1, 2, 3, 4])
    def test_repeated_broadcasts_remain_stable(self, node_pair, count):
        a, _ = node_pair
        for idx in range(count):
            a.broadcast(f"m-{idx}")
        assert len(a._broadcast_log) == count


class TestNetworkTopology:
    def test_add_node(self):
        topo = NetworkTopology()
        node = PentadNetworkNode("n1", "127.0.0.1", 9201)
        topo.add_node(node)
        assert topo._nodes["n1"] is node

    def test_remove_node(self):
        topo = NetworkTopology()
        node = PentadNetworkNode("n1", "127.0.0.1", 9201)
        topo.add_node(node)
        removed = topo.remove_node("n1")
        assert removed is node

    def test_remove_missing_returns_none(self):
        assert NetworkTopology().remove_node("ghost") is None

    def test_stability_zero_for_singleton(self):
        topo = NetworkTopology()
        topo.add_node(PentadNetworkNode("n1", "127.0.0.1", 9201))
        assert topo.get_topology_stability() == 0.0

    def test_stability_bounded_for_pair(self, node_pair):
        a, b = node_pair
        topo = NetworkTopology()
        topo.add_node(a)
        topo.add_node(b)
        assert 0.0 <= topo.get_topology_stability() <= 1.0

    @pytest.mark.parametrize("n_nodes", [2, 3, 4, 5, 6])
    def test_stability_computable_for_meshes(self, n_nodes):
        topo = NetworkTopology()
        nodes = [
            PentadNetworkNode(f"n{i}", "127.0.0.1", 9300 + i) for i in range(n_nodes)
        ]
        for node in nodes:
            topo.add_node(node)
        for left, right in zip(nodes, nodes[1:]):
            left.connect(right)
        assert 0.0 <= topo.get_topology_stability() <= 1.0


class TestCommandParser:
    @pytest.mark.parametrize(
        ("raw", "command", "args"),
        [
            ("status", "status", []),
            ("alert human warn", "alert", ["human", "warn"]),
            ("reset", "reset", []),
            ("help", "help", []),
            (" status now ", "status", ["now"]),
            ("alert ai failure immediate", "alert", ["ai", "failure", "immediate"]),
            ("", "", []),
            ("   ", "", []),
        ],
    )
    def test_parse(self, raw, command, args):
        parsed = CommandParser().parse(raw)
        assert parsed["command"] == command
        assert parsed["args"] == args


class TestPentadShell:
    @pytest.fixture()
    def shell(self):
        return PentadShell()

    def test_status_returns_counts(self, shell):
        result = shell.execute("status")
        assert result["command"] == "status"

    def test_help_lists_commands(self, shell):
        result = shell.execute("help")
        assert "alert" in result["commands"]

    def test_alert_records_alert(self, shell):
        result = shell.execute("alert human warning")
        assert result["alerts"] == 1

    def test_reset_clears_alerts(self, shell):
        shell.execute("alert human warning")
        shell.execute("reset")
        assert shell.execute("status")["alerts"] == 0

    def test_history_records_commands(self, shell):
        shell.execute("status")
        shell.execute("help")
        assert shell.get_history() == ["status", "help"]

    def test_alert_requires_args(self, shell):
        with pytest.raises(ValueError):
            shell.execute("alert human")

    def test_unknown_command_raises(self, shell):
        with pytest.raises(ValueError):
            shell.execute("launch")

    @pytest.mark.parametrize("cmd", ["status", "help", "reset"])
    def test_simple_commands_execute(self, shell, cmd):
        assert shell.execute(cmd)["command"] == cmd

    @pytest.mark.parametrize(
        "cmd",
        [
            "alert human warning",
            "alert ai error",
            "alert trust low",
            "alert brain drift",
        ],
    )
    def test_multiple_alert_forms_execute(self, shell, cmd):
        assert shell.execute(cmd)["command"] == "alert"

    def test_reset_count_increments(self, shell):
        shell.execute("reset")
        shell.execute("reset")
        assert shell.execute("status")["reset_count"] == 2

    def test_history_includes_reset(self, shell):
        shell.execute("reset")
        assert shell.get_history()[-1] == "reset"

    def test_status_history_depth_matches(self, shell):
        shell.execute("status")
        shell.execute("help")
        assert shell.execute("status")["history"] == 3


class TestEntropyAndSentinelProfilers:
    def test_start_end_profile_records_duration(self):
        profiler = EntropyProfiler()
        profiler.start_profile("shell")
        time.sleep(0.001)
        assert profiler.end_profile("shell") >= 0.0

    def test_end_without_start_raises(self):
        with pytest.raises(KeyError):
            EntropyProfiler().end_profile("ghost")

    def test_entropy_load_non_negative(self):
        profiler = EntropyProfiler()
        profiler.start_profile("network")
        profiler.end_profile("network")
        assert profiler.get_entropy_load("network") >= 0.0

    def test_profile_report_contains_label(self):
        profiler = EntropyProfiler()
        profiler.start_profile("stack")
        profiler.end_profile("stack")
        assert "stack" in profiler.get_profile_report()

    @pytest.mark.parametrize("label", ["net", "shell", "profiler", "consensus"])
    def test_profile_report_contains_duration_and_entropy(self, label):
        profiler = EntropyProfiler()
        profiler.start_profile(label)
        profiler.end_profile(label)
        report = profiler.get_profile_report()[label]
        assert "duration" in report and "entropy_load" in report

    def test_record_load(self):
        profiler = SentinelProfiler()
        profiler.record_load("axiom-1", 0.1)
        assert profiler._loads["axiom-1"] == [0.1]

    def test_overloaded_axiom_detected(self):
        profiler = SentinelProfiler()
        profiler.record_load("axiom-1", SENTINEL_CAPACITY + 0.01)
        assert profiler.get_overloaded_axioms() == ["axiom-1"]

    def test_non_overloaded_axiom_ignored(self):
        profiler = SentinelProfiler()
        profiler.record_load("axiom-1", SENTINEL_CAPACITY - 0.01)
        assert profiler.get_overloaded_axioms() == []

    @pytest.mark.parametrize("load", [0.0, 0.1, BRAIDED_SOUND_SPEED, 0.5])
    def test_record_varied_loads(self, load):
        profiler = SentinelProfiler()
        profiler.record_load("axiom", load)
        assert profiler._loads["axiom"][-1] == pytest.approx(load)

    @pytest.mark.parametrize("axiom", ["truth", "harm", "agency", "ground", "trust"])
    def test_multiple_axioms_can_be_tracked(self, axiom):
        profiler = SentinelProfiler()
        profiler.record_load(axiom, 0.2)
        assert axiom in profiler._loads


class TestIntegratedUOSStack:
    def test_shell_alert_can_be_profiled(self):
        shell = PentadShell()
        profiler = EntropyProfiler()
        profiler.start_profile("alert")
        result = shell.execute("alert human warning")
        profiler.end_profile("alert")
        assert result["alerts"] == 1
        assert profiler.get_entropy_load("alert") >= 0.0

    def test_network_broadcast_can_be_profiled(self, node_pair):
        a, _ = node_pair
        profiler = EntropyProfiler()
        profiler.start_profile("broadcast")
        sent = a.broadcast("status")
        profiler.end_profile("broadcast")
        assert sent == 1

    def test_shell_history_and_network_can_coexist(self, node_pair):
        a, _ = node_pair
        shell = PentadShell()
        shell.execute("status")
        a.broadcast("status")
        assert shell.get_history()[-1] == "status"

    def test_topology_stability_after_broadcast(self):
        a = PentadNetworkNode("a", "127.0.0.1", 9401)
        b = PentadNetworkNode("b", "127.0.0.1", 9402)
        c = PentadNetworkNode("c", "127.0.0.1", 9403)
        a.connect(b)
        b.connect(c)
        topo = NetworkTopology()
        for node in (a, b, c):
            topo.add_node(node)
        a.broadcast("mesh")
        assert 0.0 <= topo.get_topology_stability() <= 1.0

    def test_shell_reset_interacts_with_profiler(self):
        shell = PentadShell()
        profiler = EntropyProfiler()
        profiler.start_profile("reset")
        shell.execute("reset")
        profiler.end_profile("reset")
        assert "reset" in profiler.get_profile_report()

    @pytest.mark.parametrize("body", ["univ", "brain", "human", "ai", "trust"])
    def test_alerts_cover_all_bodies(self, body):
        shell = PentadShell()
        result = shell.execute(f"alert {body} diagnostic")
        assert result["record"]["body_id"] == body

    @pytest.mark.parametrize("n_links", [1, 2, 3, 4, 5])
    def test_network_scaling_stays_bounded(self, n_links):
        root = PentadNetworkNode("root", "127.0.0.1", 9500)
        topo = NetworkTopology()
        topo.add_node(root)
        for idx in range(n_links):
            peer = PentadNetworkNode(f"p{idx}", "127.0.0.1", 9501 + idx)
            topo.add_node(peer)
            root.connect(peer)
        root.broadcast("fanout")
        assert 0.0 <= root.get_network_entropy() <= 1.0

    def test_capacity_constant_matches_braided_bound(self):
        assert SENTINEL_CAPACITY == pytest.approx(BRAIDED_SOUND_SPEED)

    def test_winding_number_remains_five(self):
        assert WINDING_NUMBER == 5
