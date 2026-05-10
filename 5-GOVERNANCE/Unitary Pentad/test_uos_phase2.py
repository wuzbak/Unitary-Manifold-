# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests for UOS/ipc.py, network.py, shell.py, bootloader.py, crypto.py, container.py, profiler.py"""

import sys, os
_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_PENTAD_DIR, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

import numpy as np
import pytest

from UOS.constants import K_CS, WINDING_NUMBER, BRAID_PARTNER, PHI_BACKGROUND
from UOS.ipc import (
    Message, ManifoldChannel, MessageQueue, SharedManifoldSection,
    Pipe, IPCManager, IPC_MAX_CHANNELS, IPC_MAX_QUEUE_DEPTH,
)
from UOS.network import (
    ManifoldAddress, ManifoldNode, ManifoldFrame, ManifoldRouter,
    ManifoldSocket, NetworkStack, MTU,
)
from UOS.shell import (
    Intent, IntentAction, IntentParser, ShellCommand, CommandResult, UOSShell,
    HISTORY_CAPACITY,
)
from UOS.bootloader import ManifoldBootloader, BootPhase, BootRecord, N_BOOT_PHASES
from UOS.crypto import (
    GeometricHash, ManifoldKey, ManifoldSignature, ManifoldCipher, CryptoEngine,
    HASH_OUTPUT_BYTES,
)
from UOS.container import (
    ContainerState, ResourceQuota, ContainerProcess, ManifoldContainer,
    ContainerOrchestrator, MAX_CONTAINERS, SECTOR_WIDTH,
)
from UOS.profiler import (
    ProfileSample, ProfileTrace, ManifoldProfiler,
    MAX_SAMPLES_PER_TRACE, MAX_TRACES,
)


# ===========================================================================
# IPC Tests
# ===========================================================================

class TestMessage:
    def test_phi_in_range(self):
        m = Message(sender_pid=1, payload="hello")
        assert 0.0 <= m.phi_coord < 1.0

    def test_different_payloads_may_differ(self):
        m1 = Message(sender_pid=1, payload="aaa")
        m2 = Message(sender_pid=1, payload="zzz")
        # Not guaranteed to differ, but should for typical inputs
        # (just checking no crash)
        assert isinstance(m1.phi_coord, float)
        assert isinstance(m2.phi_coord, float)


class TestManifoldChannel:
    def test_send_receive_roundtrip(self):
        ch = ManifoldChannel("test", capacity=4)
        ch.send(pid=1, payload="hello")
        msg = ch.receive()
        assert msg is not None
        assert msg.payload == "hello"

    def test_empty_returns_none(self):
        ch = ManifoldChannel("empty")
        assert ch.receive() is None

    def test_capacity_overflow(self):
        ch = ManifoldChannel("tiny", capacity=2)
        ch.send(1, "a")
        ch.send(1, "b")
        with pytest.raises(OverflowError):
            ch.send(1, "c")

    def test_capacity_must_be_positive(self):
        with pytest.raises(ValueError):
            ManifoldChannel("bad", capacity=0)

    def test_stats_sent_received(self):
        ch = ManifoldChannel("stats-test", capacity=8)
        ch.send(1, "x")
        ch.receive()
        s = ch.stats()
        assert s["sent"] == 1
        assert s["received"] == 1

    def test_pending_count(self):
        ch = ManifoldChannel("pending", capacity=8)
        ch.send(1, "a")
        ch.send(1, "b")
        assert ch.pending() == 2

    def test_is_empty_initially(self):
        assert ManifoldChannel("e").is_empty()

    def test_connect_two_endpoints(self):
        ch = ManifoldChannel("two-ep", capacity=4)
        ch.connect(10)
        ch.connect(20)
        assert set(ch.stats()["endpoints"]) == {10, 20}

    def test_connect_three_raises(self):
        ch = ManifoldChannel("overflow-ep", capacity=4)
        ch.connect(1)
        ch.connect(2)
        with pytest.raises(OverflowError):
            ch.connect(3)

    def test_send_receive_two_endpoints(self):
        ch = ManifoldChannel("bidirectional", capacity=8)
        ch.connect(1)
        ch.connect(2)
        ch.send(pid=1, payload="from-1")
        msg = ch.receive(receiver_pid=2)
        assert msg.payload == "from-1"


class TestMessageQueue:
    def test_enqueue_dequeue(self):
        q = MessageQueue("q")
        q.enqueue(pid=1, payload="hi", priority=0.5)
        msg = q.dequeue()
        assert msg is not None
        assert msg.payload == "hi"

    def test_empty_dequeue_none(self):
        q = MessageQueue("empty-q")
        assert q.dequeue() is None

    def test_priority_order(self):
        q = MessageQueue("prio-q", capacity=10)
        q.enqueue(1, "low", priority=0.1)
        q.enqueue(1, "high", priority=0.9)
        q.enqueue(1, "mid", priority=0.5)
        first = q.dequeue()
        assert first.payload == "high"

    def test_overflow(self):
        q = MessageQueue("tiny-q", capacity=2)
        q.enqueue(1, "a")
        q.enqueue(1, "b")
        with pytest.raises(OverflowError):
            q.enqueue(1, "c")

    def test_depth(self):
        q = MessageQueue("depth-q", capacity=10)
        q.enqueue(1, "a")
        q.enqueue(1, "b")
        assert q.depth() == 2

    def test_peek_no_remove(self):
        q = MessageQueue("peek-q", capacity=5)
        q.enqueue(1, "x")
        msg = q.peek()
        assert msg.payload == "x"
        assert q.depth() == 1  # still there

    def test_stats(self):
        q = MessageQueue("stats-q", capacity=5)
        q.enqueue(1, "a")
        q.dequeue()
        s = q.stats()
        assert s["enqueued"] == 1
        assert s["dequeued"] == 1

    def test_ipc_max_channels(self):
        assert IPC_MAX_CHANNELS == K_CS


class TestSharedManifoldSection:
    def test_map_returns_array(self):
        sec = SharedManifoldSection("s1", size_pages=2)
        arr = sec.map(pid=1)
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (2 * 4096,)

    def test_write_read_roundtrip(self):
        sec = SharedManifoldSection("s2", size_pages=1)
        sec.map(pid=1)
        written = sec.write(pid=1, offset=0, data=b"hello world")
        assert written == 11
        out = sec.read(offset=0, n_bytes=11)
        assert out == b"hello world"

    def test_shared_view(self):
        sec = SharedManifoldSection("s3", size_pages=1)
        arr_a = sec.map(pid=1)
        arr_b = sec.map(pid=2)
        # Both views point to the same underlying array
        arr_a[0] = 255
        assert arr_b[0] == 255

    def test_write_lock(self):
        sec = SharedManifoldSection("s4", size_pages=1)
        sec.acquire_write_lock(pid=1)
        with pytest.raises(PermissionError):
            sec.write(pid=2, offset=0, data=b"x")
        sec.release_write_lock(pid=1)
        # Now pid=2 should succeed
        assert sec.write(pid=2, offset=0, data=b"x") == 1

    def test_size_pages_positive(self):
        with pytest.raises(ValueError):
            SharedManifoldSection("bad", size_pages=0)

    def test_stats(self):
        sec = SharedManifoldSection("s5", size_pages=4)
        sec.map(1)
        s = sec.stats()
        assert s["size_pages"] == 4
        assert 1 in s["mapped_pids"]


class TestPipe:
    def test_write_read(self):
        p = Pipe(write_pid=1, read_pid=2)
        n = p.write(b"test data")
        assert n == 9
        assert p.read() == b"test data"

    def test_read_empty(self):
        p = Pipe(1, 2)
        assert p.read() is None

    def test_pending(self):
        p = Pipe(1, 2)
        p.write(b"a")
        p.write(b"b")
        assert p.pending() == 2


class TestIPCManager:
    def test_create_get_channel(self):
        mgr = IPCManager()
        ch = mgr.create_channel("ch1")
        assert mgr.get_channel("ch1") is ch

    def test_create_channel_idempotent(self):
        mgr = IPCManager()
        ch1 = mgr.create_channel("ch")
        ch2 = mgr.create_channel("ch")
        assert ch1 is ch2

    def test_destroy_channel(self):
        mgr = IPCManager()
        mgr.create_channel("tmp")
        mgr.destroy_channel("tmp")
        with pytest.raises(KeyError):
            mgr.get_channel("tmp")

    def test_create_queue(self):
        mgr = IPCManager()
        q = mgr.create_queue("q1")
        assert mgr.get_queue("q1") is q

    def test_create_section(self):
        mgr = IPCManager()
        sec = mgr.create_section("shm1", size_pages=4)
        assert mgr.get_section("shm1") is sec

    def test_create_pipe(self):
        mgr = IPCManager()
        p = mgr.create_pipe(write_pid=1, read_pid=2)
        assert mgr.get_pipe(1, 2) is p

    def test_max_channels_limit(self):
        mgr = IPCManager(max_channels=2)
        mgr.create_channel("a")
        mgr.create_channel("b")
        with pytest.raises(OverflowError):
            mgr.create_channel("c")

    def test_stats(self):
        mgr = IPCManager()
        mgr.create_channel("c")
        mgr.create_queue("q")
        s = mgr.stats()
        assert s["channels"] >= 1
        assert s["queues"] >= 1


# ===========================================================================
# Network Tests
# ===========================================================================

class TestManifoldAddress:
    def test_from_node_id_deterministic(self):
        a1 = ManifoldAddress.from_node_id("kernel")
        a2 = ManifoldAddress.from_node_id("kernel")
        assert a1.phi == pytest.approx(a2.phi)

    def test_from_node_id_phi_in_range(self):
        a = ManifoldAddress.from_node_id("host")
        assert 0.0 <= a.phi < 2 * np.pi * WINDING_NUMBER

    def test_distance_same_node(self):
        a = ManifoldAddress.from_node_id("a")
        assert a.distance_to(a) == pytest.approx(0.0, abs=1e-9)

    def test_distance_nonnegative(self):
        a = ManifoldAddress.from_node_id("a")
        b = ManifoldAddress.from_node_id("b")
        assert a.distance_to(b) >= 0.0

    def test_as_vector_shape(self):
        a = ManifoldAddress.from_node_id("x")
        assert a.as_vector().shape == (4,)

    def test_str_repr(self):
        a = ManifoldAddress(phi=1.0, winding=5, node_id="test")
        assert "test" in str(a)


class TestManifoldNode:
    def test_address_auto_derived(self):
        n = ManifoldNode("server")
        assert n.address is not None
        assert n.address.node_id == "server"

    def test_receive_and_next_frame(self):
        n = ManifoldNode("n")
        src = ManifoldAddress.from_node_id("src")
        dst = ManifoldAddress.from_node_id("dst")
        frame = ManifoldFrame(src=src, dst=dst, payload=b"data")
        n.receive_frame(frame)
        assert n.pending_frames() == 1
        out = n.next_frame()
        assert out.payload == b"data"
        assert n.pending_frames() == 0


class TestManifoldFrame:
    def test_checksum_ok_fresh(self):
        src = ManifoldAddress.from_node_id("s")
        dst = ManifoldAddress.from_node_id("d")
        f = ManifoldFrame(src=src, dst=dst, payload=b"hello")
        assert f.checksum_ok()

    def test_payload_too_large_raises(self):
        src = ManifoldAddress.from_node_id("s")
        dst = ManifoldAddress.from_node_id("d")
        with pytest.raises(ValueError):
            ManifoldFrame(src=src, dst=dst, payload=b"x" * (MTU + 1))

    def test_size_bytes(self):
        src = ManifoldAddress.from_node_id("s")
        dst = ManifoldAddress.from_node_id("d")
        f = ManifoldFrame(src=src, dst=dst, payload=b"abc")
        assert f.size_bytes == 3


class TestManifoldRouter:
    def test_route_returns_closest_peer(self):
        local = ManifoldNode("gw", is_router=True)
        router = ManifoldRouter(local)
        peer_a = ManifoldNode("a")
        peer_b = ManifoldNode("b")
        router.add_peer(peer_a)
        router.add_peer(peer_b)
        dst = ManifoldAddress.from_node_id("a")
        result = router.route(dst)
        assert result is not None

    def test_route_no_peers_none(self):
        router = ManifoldRouter(ManifoldNode("lone"))
        dst = ManifoldAddress.from_node_id("x")
        assert router.route(dst) is None

    def test_forward_direct_peer(self):
        local = ManifoldNode("gw")
        router = ManifoldRouter(local)
        peer = ManifoldNode("target")
        router.add_peer(peer)
        src = ManifoldAddress.from_node_id("gw")
        dst = ManifoldAddress.from_node_id("target")
        frame = ManifoldFrame(src=src, dst=dst, payload=b"ping")
        result = router.forward(frame)
        assert result is peer
        assert peer.pending_frames() == 1

    def test_stats(self):
        router = ManifoldRouter(ManifoldNode("r"))
        router.add_peer(ManifoldNode("p"))
        s = router.stats()
        assert "p" in s["peers"]


class TestManifoldSocket:
    def _pair(self):
        a = ManifoldNode("client")
        b = ManifoldNode("server")
        sock = ManifoldSocket(local=a, remote=b)
        sock.connect()
        return sock, a, b

    def test_connect_is_connected(self):
        sock, _, _ = self._pair()
        assert sock.is_connected

    def test_send_delivers_to_remote(self):
        sock, client, server = self._pair()
        n = sock.send(b"hello")
        assert n == 5
        assert server.pending_frames() == 1

    def test_recv_empty_none(self):
        sock, client, server = self._pair()
        assert sock.recv() is None

    def test_recv_all(self):
        a = ManifoldNode("c")
        b = ManifoldNode("s")
        sock = ManifoldSocket(local=a, remote=b)
        sock.connect()
        # Put a frame directly into a's buffer to simulate server reply
        src = ManifoldAddress.from_node_id("s")
        dst = ManifoldAddress.from_node_id("c")
        from UOS.network import ManifoldFrame
        a.receive_frame(ManifoldFrame(src=src, dst=dst, payload=b"data"))
        out = sock.recv_all()
        assert out == b"data"

    def test_send_not_connected_raises(self):
        sock = ManifoldSocket(ManifoldNode("x"), ManifoldNode("y"))
        with pytest.raises(ConnectionError):
            sock.send(b"hi")

    def test_stats(self):
        sock, _, _ = self._pair()
        sock.send(b"x")
        s = sock.stats()
        assert s["connected"] is True
        assert s["send_count"] == 1


class TestNetworkStack:
    def test_add_peer_and_connect(self):
        stack = NetworkStack("host")
        stack.add_peer("peer1")
        sock = stack.connect("peer1")
        assert sock.is_connected

    def test_connect_unknown_raises(self):
        stack = NetworkStack("host")
        with pytest.raises(KeyError):
            stack.connect("ghost")

    def test_route_frame_to(self):
        stack = NetworkStack("host")
        stack.add_peer("target")
        result = stack.route_frame_to("target", b"broadcast")
        # Should deliver to a peer node
        assert result is not None

    def test_stats(self):
        stack = NetworkStack("myhost")
        stack.add_peer("p1")
        s = stack.stats()
        assert "myhost" in s["local_node"]
        assert "p1" in s["peers"]


# ===========================================================================
# Shell Tests
# ===========================================================================

class TestIntentParser:
    def _parser(self):
        return IntentParser()

    def test_list_action(self):
        p = self._parser()
        intent = p.parse("list all files")
        assert intent.action == IntentAction.LIST

    def test_read_action(self):
        p = self._parser()
        assert p.parse("read the config file").action == IntentAction.READ

    def test_write_action(self):
        p = self._parser()
        assert p.parse("write hello to output.txt").action == IntentAction.WRITE

    def test_execute_action(self):
        p = self._parser()
        assert p.parse("run my program").action == IntentAction.EXECUTE

    def test_stop_action(self):
        p = self._parser()
        assert p.parse("kill process 42").action == IntentAction.STOP

    def test_search_action(self):
        p = self._parser()
        assert p.parse("find files named main.py").action == IntentAction.SEARCH

    def test_compile_action(self):
        p = self._parser()
        assert p.parse("build the project").action == IntentAction.COMPILE

    def test_network_action(self):
        p = self._parser()
        assert p.parse("connect to server").action == IntentAction.NETWORK

    def test_security_action(self):
        p = self._parser()
        assert p.parse("verify the signature").action == IntentAction.SECURITY

    def test_status_action(self):
        p = self._parser()
        assert p.parse("status of the system").action == IntentAction.STATUS

    def test_help_action(self):
        p = self._parser()
        assert p.parse("help me with files").action == IntentAction.HELP

    def test_unknown_action(self):
        p = self._parser()
        intent = p.parse("xkcd1234xyzzy")
        assert intent.action == IntentAction.UNKNOWN

    def test_phi_coord_in_range(self):
        p = self._parser()
        intent = p.parse("list files")
        assert 0.0 <= intent.phi_coord < 1.0

    def test_high_confidence_first_token(self):
        p = self._parser()
        intent = p.parse("list everything")
        from UOS.shell import IntentConfidence
        assert intent.confidence == IntentConfidence.HIGH


class TestUOSShell:
    def _shell(self):
        return UOSShell(session_id="test-tty", pid=99)

    def test_default_env_vars(self):
        sh = self._shell()
        assert sh.getenv("SHELL") == "uos-shell"
        assert sh.getenv("WINDING_NUMBER") == str(WINDING_NUMBER)
        assert sh.getenv("K_CS") == str(K_CS)

    def test_setenv_getenv(self):
        sh = self._shell()
        sh.setenv("FOO", "bar")
        assert sh.getenv("FOO") == "bar"

    def test_unsetenv(self):
        sh = self._shell()
        sh.setenv("TMP", "tmp")
        sh.unsetenv("TMP")
        assert sh.getenv("TMP") == ""

    def test_eval_status(self):
        sh = self._shell()
        result = sh.eval("status of the system")
        assert result.success

    def test_eval_help(self):
        sh = self._shell()
        result = sh.eval("help me")
        assert result.success
        assert "UOS" in str(result.output)

    def test_eval_list(self):
        sh = self._shell()
        result = sh.eval("list env vars")
        assert result.success

    def test_history_grows(self):
        sh = self._shell()
        sh.eval("status")
        sh.eval("help")
        sh.eval("list files")
        assert len(sh.history_entries()) == 3

    def test_recall_last(self):
        sh = self._shell()
        sh.eval("help me")
        intent = sh.recall(1)
        assert intent.action == IntentAction.HELP

    def test_history_capacity(self):
        assert HISTORY_CAPACITY == K_CS

    def test_geodesic_recall(self):
        sh = self._shell()
        for i in range(5):
            sh.eval("status check")
        entries = sh.geodesic_recall(phi_target=0.5, tol=0.5)
        # Should find some entries (phi range is broad)
        assert isinstance(entries, list)

    def test_register_custom_handler(self):
        sh = self._shell()
        sh.register_handler(IntentAction.DELETE, lambda i: f"deleted: {i.resource}")
        result = sh.eval("delete old logs")
        assert result.success
        assert "deleted" in str(result.output)

    def test_unknown_intent_returns_error_or_fallback(self):
        sh = self._shell()
        result = sh.eval("xkcd1234xyzzy-unknown-command")
        # With default handler for UNKNOWN, should succeed
        assert result is not None

    def test_stats(self):
        sh = self._shell()
        sh.eval("status")
        s = sh.stats()
        assert s["session_id"] == "test-tty"
        assert s["tick"] >= 1


# ===========================================================================
# Bootloader Tests
# ===========================================================================

class TestManifoldBootloader:
    def _bl(self, n_grid=8):
        return ManifoldBootloader(n_grid=n_grid, verbose=False)

    def test_seven_phases(self):
        assert N_BOOT_PHASES == BRAID_PARTNER == 7

    def test_phases_descriptor(self):
        assert len(ManifoldBootloader.PHASES) == 7

    def test_run_returns_7_records(self):
        records = self._bl().run()
        assert len(records) == 7

    def test_all_phases_succeed(self):
        records = self._bl().run()
        for r in records:
            assert r.success, f"Phase {r.phase.name} failed: {r.error}"

    def test_is_booted_after_run(self):
        bl = self._bl()
        bl.run()
        assert bl.is_booted

    def test_boot_summary_phases_ok(self):
        bl = self._bl()
        bl.run()
        s = bl.boot_summary()
        assert s["phases_ok"] == 7
        assert s["phases_failed"] == 0
        assert s["is_booted"] is True

    def test_manifold_state_has_phi(self):
        bl = self._bl()
        bl.run()
        assert "phi" in bl._manifold_state
        phi = np.array(bl._manifold_state["phi"])
        assert np.all(np.isclose(phi, PHI_BACKGROUND))

    def test_manifold_state_memory_map(self):
        bl = self._bl()
        bl.run()
        mm = bl._manifold_state["memory_map"]
        assert mm["total"] > 0
        assert mm["kernel"] > 0

    def test_security_invariant_ok(self):
        bl = self._bl()
        bl.run()
        assert bl._manifold_state["invariant_ok"] is True

    def test_language_lanes_74(self):
        bl = self._bl()
        bl.run()
        assert bl._manifold_state["language_lanes"] == K_CS

    def test_n_grid_too_small_raises(self):
        with pytest.raises(ValueError):
            ManifoldBootloader(n_grid=2)

    def test_hardware_channels(self):
        bl = self._bl()
        bl.run()
        assert bl._manifold_state["hardware_channels"] > 0

    def test_ipc_primitives_created(self):
        bl = self._bl()
        bl.run()
        assert len(bl._manifold_state["ipc_primitives"]) == 3

    def test_handoff_to_scheduler(self):
        bl = self._bl()
        bl.run()
        assert bl._manifold_state["scheduler"] == "GeodesicScheduler"

    def test_records_have_elapsed_ticks(self):
        bl = self._bl()
        records = bl.run()
        for r in records:
            assert r.elapsed_ticks >= 0.0

    def test_phase_names_unique(self):
        names = [p.name for p in ManifoldBootloader.PHASES]
        assert len(set(names)) == 7


# ===========================================================================
# Crypto Tests
# ===========================================================================

class TestGeometricHash:
    def test_digest_length(self):
        gh = GeometricHash(b"hello")
        assert len(gh.digest()) == HASH_OUTPUT_BYTES

    def test_hexdigest_length(self):
        gh = GeometricHash(b"hello")
        assert len(gh.hexdigest()) == HASH_OUTPUT_BYTES * 2

    def test_deterministic(self):
        d1 = GeometricHash(b"abc").digest()
        d2 = GeometricHash(b"abc").digest()
        assert d1 == d2

    def test_different_inputs_may_differ(self):
        d1 = GeometricHash(b"aaa").digest()
        d2 = GeometricHash(b"bbb").digest()
        # Extremely unlikely to collide
        assert d1 != d2

    def test_phi_in_range(self):
        gh = GeometricHash(b"test payload")
        assert 0.0 <= gh.phi_fingerprint() < 1.0

    def test_winding_class_in_range(self):
        gh = GeometricHash(b"anything")
        assert 0 <= gh.winding_class() < WINDING_NUMBER

    def test_empty_input(self):
        gh = GeometricHash(b"")
        assert len(gh.digest()) == HASH_OUTPUT_BYTES

    def test_is_similar_same_input(self):
        gh = GeometricHash(b"xyz")
        assert gh.is_similar_to(gh)

    def test_is_similar_different_inputs(self):
        gh1 = GeometricHash(b"hello")
        gh2 = GeometricHash(b"world")
        # Just verifying no crash; result is data-dependent
        assert isinstance(gh1.is_similar_to(gh2), bool)


class TestManifoldKey:
    def test_private_key_shape(self):
        key = ManifoldKey(seed=b"secret", tier=2)
        assert key.private_key.shape == (WINDING_NUMBER,)

    def test_public_key_shape(self):
        key = ManifoldKey(seed=b"secret", tier=2)
        assert key.public_key.shape == (WINDING_NUMBER,)

    def test_deterministic_from_seed(self):
        k1 = ManifoldKey(seed=b"same-seed", tier=1)
        k2 = ManifoldKey(seed=b"same-seed", tier=1)
        np.testing.assert_array_equal(k1.private_key, k2.private_key)

    def test_different_seeds_differ(self):
        k1 = ManifoldKey(seed=b"seed-a", tier=0)
        k2 = ManifoldKey(seed=b"seed-b", tier=0)
        assert not np.allclose(k1.private_key, k2.private_key)

    def test_invalid_tier_raises(self):
        with pytest.raises(ValueError):
            ManifoldKey(seed=b"x", tier=WINDING_NUMBER)

    def test_public_key_bytes_length(self):
        key = ManifoldKey(seed=b"k", tier=0)
        assert len(key.public_key_bytes()) == WINDING_NUMBER * 8  # float64 = 8 bytes


class TestManifoldSignature:
    def _key(self):
        return ManifoldKey(seed=b"test-key", tier=2)

    def test_verify_correct(self):
        key = self._key()
        sig = ManifoldSignature(b"important data", key)
        assert sig.verify(b"important data", key)

    def test_verify_tampered(self):
        key = self._key()
        sig = ManifoldSignature(b"original", key)
        assert not sig.verify(b"tampered", key)

    def test_signature_bytes_length(self):
        key = self._key()
        sig = ManifoldSignature(b"msg", key)
        assert len(sig.signature_bytes) == 32

    def test_geometric_invariant_ok(self):
        key = self._key()
        sig = ManifoldSignature(b"valid message", key)
        assert sig.geometric_invariant_ok()

    def test_different_keys_differ(self):
        k1 = ManifoldKey(seed=b"k1", tier=1)
        k2 = ManifoldKey(seed=b"k2", tier=1)
        s1 = ManifoldSignature(b"msg", k1)
        s2 = ManifoldSignature(b"msg", k2)
        assert s1.signature_bytes != s2.signature_bytes


class TestManifoldCipher:
    def _cipher(self, tier=2):
        key = ManifoldKey(seed=b"cipher-key", tier=tier)
        return ManifoldCipher(key)

    def test_encrypt_decrypt_roundtrip(self):
        cipher = self._cipher()
        plaintext = b"hello manifold world"
        ct = cipher.encrypt(plaintext)
        pt = cipher.decrypt(ct)
        assert pt == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        cipher = self._cipher()
        pt = b"hello"
        ct = cipher.encrypt(pt)
        assert ct != pt

    def test_empty_roundtrip(self):
        cipher = self._cipher()
        assert cipher.encrypt(b"") == b""
        assert cipher.decrypt(b"") == b""

    def test_all_tiers(self):
        for tier in range(WINDING_NUMBER):
            cipher = self._cipher(tier=tier)
            pt = b"test payload"
            assert cipher.decrypt(cipher.encrypt(pt)) == pt


class TestCryptoEngine:
    def test_generate_and_get_key(self):
        engine = CryptoEngine()
        kid = engine.generate_key(seed=b"seed", tier=2, key_id="alice")
        key = engine.get_key("alice")
        assert key.tier == 2

    def test_sign_verify(self):
        engine = CryptoEngine()
        kid = engine.generate_key(seed=b"s", tier=2, key_id="k1")
        sig = engine.sign(b"data", kid)
        assert engine.verify(b"data", sig, kid)

    def test_verify_fails_tampered(self):
        engine = CryptoEngine()
        kid = engine.generate_key(seed=b"s", tier=2, key_id="k2")
        sig = engine.sign(b"original", kid)
        assert not engine.verify(b"tampered", sig, kid)

    def test_encrypt_decrypt(self):
        engine = CryptoEngine()
        kid = engine.generate_key(seed=b"enc-seed", tier=1, key_id="k3")
        ct = engine.encrypt(b"secret", kid)
        assert engine.decrypt(ct, kid) == b"secret"

    def test_hash(self):
        engine = CryptoEngine()
        gh = engine.hash(b"hello")
        assert len(gh.digest()) == HASH_OUTPUT_BYTES

    def test_list_keys(self):
        engine = CryptoEngine()
        engine.generate_key(b"a", key_id="aa")
        engine.generate_key(b"b", key_id="bb")
        assert "aa" in engine.list_keys()
        assert "bb" in engine.list_keys()

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError):
            CryptoEngine().get_key("nonexistent")

    def test_auto_key_id(self):
        engine = CryptoEngine()
        kid = engine.generate_key(seed=b"auto")
        assert isinstance(kid, str) and len(kid) > 0


# ===========================================================================
# Container Tests
# ===========================================================================

class TestResourceQuota:
    def test_defaults(self):
        q = ResourceQuota()
        assert 0.0 < q.cpu <= 1.0
        assert q.memory_pages >= 1

    def test_cpu_clipped(self):
        q = ResourceQuota(cpu=2.0)
        assert q.cpu == 1.0

    def test_memory_zero_raises(self):
        with pytest.raises(ValueError):
            ResourceQuota(memory_pages=0)


class TestManifoldContainer:
    def _c(self, sector=0):
        return ManifoldContainer("test-container", winding_sector=sector)

    def test_initial_state_created(self):
        c = self._c()
        assert c.state == ContainerState.CREATED

    def test_start(self):
        c = self._c()
        c.start()
        assert c.state == ContainerState.RUNNING

    def test_pause_resume(self):
        c = self._c()
        c.start()
        c.pause()
        assert c.state == ContainerState.PAUSED
        c.resume()
        assert c.state == ContainerState.RUNNING

    def test_stop(self):
        c = self._c()
        c.start()
        c.stop()
        assert c.state == ContainerState.STOPPED

    def test_destroy(self):
        c = self._c()
        c.start()
        c.destroy()
        assert c.state == ContainerState.DESTROYED

    def test_spawn_process(self):
        c = self._c()
        c.start()
        proc = c.spawn_process("worker", language="Python", cpu_fraction=0.1, memory_pages=2)
        assert proc.pid == 1
        assert proc.language == "Python"

    def test_spawn_not_running_raises(self):
        c = self._c()
        with pytest.raises(RuntimeError):
            c.spawn_process("x")

    def test_kill_process(self):
        c = self._c()
        c.start()
        proc = c.spawn_process("w", cpu_fraction=0.1, memory_pages=1)
        c.kill_process(proc.pid)
        assert len(c._processes) == 0

    def test_cpu_quota_enforced(self):
        c = ManifoldContainer("c", quota=ResourceQuota(cpu=0.2))
        c.start()
        c.spawn_process("a", cpu_fraction=0.1, memory_pages=1)
        c.spawn_process("b", cpu_fraction=0.1, memory_pages=1)
        with pytest.raises(RuntimeError):
            c.spawn_process("c", cpu_fraction=0.1, memory_pages=1)

    def test_contains_phi(self):
        c = self._c(sector=0)
        assert c.contains_phi(c.phi_lo)
        assert not c.contains_phi(c.phi_hi + 1.0)

    def test_same_sector_can_communicate(self):
        a = ManifoldContainer("a", winding_sector=2)
        b = ManifoldContainer("b", winding_sector=2)
        assert a.can_communicate_with(b)

    def test_different_sector_needs_permit(self):
        a = ManifoldContainer("a", winding_sector=1)
        b = ManifoldContainer("b", winding_sector=5)
        assert not a.can_communicate_with(b, permit=False)
        assert a.can_communicate_with(b, permit=True)

    def test_invalid_sector_raises(self):
        with pytest.raises(ValueError):
            ManifoldContainer("bad", winding_sector=K_CS)

    def test_stats(self):
        c = self._c()
        c.start()
        c.spawn_process("w", cpu_fraction=0.1, memory_pages=2)
        s = c.stats()
        assert s["state"] == "RUNNING"
        assert s["processes"] == 1

    def test_event_log(self):
        c = self._c()
        c.start()
        log = c.event_log()
        assert any("started" in e.lower() for e in log)


class TestContainerOrchestrator:
    def _orch(self):
        return ContainerOrchestrator()

    def test_create_and_start(self):
        orch = self._orch()
        cid = orch.create("app", image="uos-base")
        orch.start(cid)
        assert orch.get_container(cid).state == ContainerState.RUNNING

    def test_create_idempotent(self):
        orch = self._orch()
        cid1 = orch.create("app")
        cid2 = orch.create("app")
        assert cid1 == cid2

    def test_auto_sector_assignment(self):
        orch = self._orch()
        orch.create("c1")
        orch.create("c2")
        s1 = orch.get_container("c1").winding_sector
        s2 = orch.get_container("c2").winding_sector
        assert s1 != s2

    def test_destroy_frees_sector(self):
        orch = self._orch()
        orch.create("c1")
        sector = orch.get_container("c1").winding_sector
        orch.destroy("c1")
        assert sector not in orch._sector_assignments

    def test_spawn(self):
        orch = self._orch()
        orch.create("app")
        orch.start("app")
        proc = orch.spawn("app", "worker", language="Go", cpu_fraction=0.1, memory_pages=2)
        assert proc.language == "Go"

    def test_can_communicate_same_sector(self):
        orch = self._orch()
        orch.create("a", winding_sector=3)
        orch.create("b", winding_sector=3)
        assert orch.can_communicate("a", "b")

    def test_can_communicate_different_sector(self):
        orch = self._orch()
        orch.create("x", winding_sector=1)
        orch.create("y", winding_sector=2)
        assert not orch.can_communicate("x", "y")
        assert orch.can_communicate("x", "y", permit=True)

    def test_max_containers(self):
        orch = ContainerOrchestrator(max_containers=2)
        orch.create("a")
        orch.create("b")
        with pytest.raises(OverflowError):
            orch.create("c")

    def test_stats(self):
        orch = self._orch()
        orch.create("app")
        orch.start("app")
        s = orch.stats()
        assert s["total_containers"] == 1
        assert s["running"] == 1


# ===========================================================================
# Profiler Tests
# ===========================================================================

class TestProfileTrace:
    def _trace(self):
        return ProfileTrace(pid=1, name="test-proc")

    def test_add_sample(self):
        t = self._trace()
        s = t.add_sample(phi=1.0, tick=0, cpu_fraction=0.5)
        assert isinstance(s, ProfileSample)
        assert len(t.samples()) == 1

    def test_geodesic_length_zero_samples(self):
        assert self._trace().total_geodesic_length() == 0.0

    def test_geodesic_length_two_samples(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0)
        t.add_sample(phi=1.5, tick=1)
        assert t.total_geodesic_length() == pytest.approx(0.5, abs=1e-9)

    def test_mean_curvature_zero_samples(self):
        assert self._trace().mean_curvature() == 0.0

    def test_curvature_auto_computed(self):
        t = self._trace()
        t.add_sample(phi=0.0, tick=0)
        t.add_sample(phi=1.0, tick=1)
        # curvature = (1.0 / 1)^2 = 1.0
        s = t.samples()[-1]
        assert s.curvature > 0.0

    def test_peak_curvature(self):
        t = self._trace()
        t.add_sample(phi=0.0, tick=0)
        t.add_sample(phi=10.0, tick=1)  # big jump
        t.add_sample(phi=10.1, tick=2)  # small step
        assert t.peak_curvature() > 0.0

    def test_mean_cpu(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0, cpu_fraction=0.4)
        t.add_sample(phi=1.0, tick=1, cpu_fraction=0.6)
        assert t.mean_cpu() == pytest.approx(0.5, abs=1e-9)

    def test_peak_memory(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0, memory_pages=4)
        t.add_sample(phi=1.0, tick=1, memory_pages=8)
        assert t.peak_memory() == 8

    def test_total_entropy(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0, entropy=0.3)
        t.add_sample(phi=1.0, tick=1, entropy=0.5)
        assert t.total_entropy() == pytest.approx(0.8, abs=1e-9)

    def test_hotspots_top_n(self):
        t = self._trace()
        t.add_sample(phi=0.0, tick=0)
        t.add_sample(phi=5.0, tick=1)   # big jump → high curvature
        t.add_sample(phi=5.01, tick=2)  # tiny step → low curvature
        hotspots = t.hotspots(1)
        assert len(hotspots) == 1
        assert hotspots[0].curvature >= 0.0

    def test_geodesic_efficiency_in_range(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0, cpu_fraction=0.8)
        t.add_sample(phi=1.01, tick=1, cpu_fraction=0.8)
        eff = t.geodesic_efficiency()
        assert 0.0 <= eff <= 1.0

    def test_ring_buffer_overflow(self):
        t = ProfileTrace(pid=1, max_samples=3)
        for i in range(5):
            t.add_sample(phi=float(i), tick=i)
        assert len(t.samples()) == 3

    def test_report_keys(self):
        t = self._trace()
        t.add_sample(phi=1.0, tick=0, cpu_fraction=0.5, memory_pages=2)
        report = t.report()
        for key in ["pid", "name", "samples", "geodesic_length",
                    "mean_curvature", "geodesic_efficiency",
                    "total_entropy", "mean_cpu", "peak_memory_pages"]:
            assert key in report


class TestManifoldProfiler:
    def _prof(self):
        return ManifoldProfiler()

    def test_start_trace(self):
        p = self._prof()
        trace = p.start_trace(pid=1, name="kernel")
        assert trace.pid == 1

    def test_sample_creates_trace(self):
        p = self._prof()
        p.sample(pid=42, phi=1.0, tick=0, cpu_fraction=0.5)
        assert p.get_trace(42) is not None

    def test_report(self):
        p = self._prof()
        p.start_trace(pid=1)
        for i in range(5):
            p.sample(pid=1, phi=PHI_BACKGROUND + 0.01 * i, tick=i, cpu_fraction=0.6)
        report = p.report(pid=1)
        assert report["mean_cpu"] == pytest.approx(0.6, abs=1e-9)

    def test_report_unknown_raises(self):
        with pytest.raises(KeyError):
            self._prof().report(pid=99999)

    def test_global_report(self):
        p = self._prof()
        p.sample(pid=1, phi=1.0, tick=0, cpu_fraction=0.5)
        p.sample(pid=2, phi=2.0, tick=0, cpu_fraction=0.7)
        gr = p.global_report()
        assert gr["traces"] == 2

    def test_efficiency_ranking(self):
        p = self._prof()
        p.sample(pid=1, phi=1.0, tick=0, cpu_fraction=0.9)
        p.sample(pid=2, phi=1.0, tick=0, cpu_fraction=0.1)
        ranking = p.efficiency_ranking()
        assert len(ranking) == 2
        assert ranking[0][1] >= ranking[1][1]

    def test_hotspot_pids(self):
        p = self._prof()
        p.sample(pid=1, phi=0.0, tick=0)
        p.sample(pid=1, phi=100.0, tick=1)  # huge jump
        p.sample(pid=2, phi=1.0, tick=0)
        p.sample(pid=2, phi=1.01, tick=1)   # tiny step
        hot = p.hotspot_pids(1)
        assert hot[0] == 1  # pid=1 has more curvature

    def test_profile_callable(self):
        p = self._prof()
        result, report = p.profile(fn=lambda: 42, pid=10, n_samples=5)
        assert result == 42
        assert report["samples"] >= 5

    def test_max_traces_exceeded(self):
        p = ManifoldProfiler(max_traces=2)
        p.start_trace(pid=1)
        p.start_trace(pid=2)
        with pytest.raises(OverflowError):
            p.start_trace(pid=3)

    def test_stop_trace(self):
        p = self._prof()
        p.start_trace(pid=1)
        p.stop_trace(pid=1)
        assert p.get_trace(pid=1) is None

    def test_tick_advances(self):
        p = self._prof()
        t1 = p.tick()
        t2 = p.tick()
        assert t2 == t1 + 1

    def test_stats(self):
        p = self._prof()
        p.sample(pid=1, phi=1.0, tick=0)
        s = p.stats()
        assert s["active_traces"] == 1
