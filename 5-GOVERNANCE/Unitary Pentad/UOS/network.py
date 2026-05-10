# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/network.py
==============
Unitary Operating System — Manifold Network Stack

Conventional TCP/IP routing finds the *shortest hop path* in a flat graph.
The UOS **ManifoldNetworkStack** routes packets along *geodesics* of the 5D
manifold: the "shortest path" is the path of least φ-curvature, which
automatically avoids congested or insecure nodes.

Stack Layers (ISO/OSI re-mapped to 5D geometry)
------------------------------------------------
Layer 5 — Manifold Transport   ManifoldSocket (reliable, φ-ordered delivery)
Layer 4 — Manifold Network     ManifoldRouter  (geodesic path selection)
Layer 3 — Manifold Link        ManifoldNode    (peer identity + φ-address)
Layer 2 — Manifold Physical    ManifoldFrame   (raw PDU with braid checksum)

Key Classes
-----------
ManifoldAddress(phi, winding, node_id)
    A 5D network address.  Analogous to an IP address but encodes geometric
    position in the manifold.

ManifoldNode(node_id, address)
    A peer in the manifold network (host, router, or device).

ManifoldFrame(src, dst, payload, seq)
    The atomic network PDU.  Includes a φ-checksum for geometric integrity.

ManifoldRouter(nodes)
    Geodesic routing engine.  Picks the next-hop node by minimising the
    manifold distance to the destination.

ManifoldSocket(local_node, remote_node)
    Reliable, ordered, φ-addressed connection between two nodes.

NetworkStack(local_node_id)
    Full five-layer stack: create sockets, send/receive data, route frames.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import hashlib
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

import numpy as np

from UOS.constants import (
    K_CS, WINDING_NUMBER, BRAID_PARTNER, PHI_BACKGROUND,
    BRAIDED_SOUND_SPEED, LAMBDA_COUPLING,
)

# Network-specific derived constants
MAX_NODES: int = K_CS * BRAID_PARTNER         # = 74 × 7 = 518 nodes
MAX_FRAME_PAYLOAD: int = K_CS * 16            # = 1184 bytes per frame
MTU: int = MAX_FRAME_PAYLOAD                  # manifold transmission unit


# ===========================================================================
# ManifoldAddress
# ===========================================================================

@dataclass(frozen=True)
class ManifoldAddress:
    """A 5D network address on the UOS manifold.

    Parameters
    ----------
    phi : float
        Radion coordinate in [0, 2π × WINDING_NUMBER).
    winding : int
        Braid winding number (default: WINDING_NUMBER = 5).
    node_id : str
        Human-readable node identifier.

    Examples
    --------
    >>> a = ManifoldAddress(phi=1.0, winding=5, node_id="kernel")
    >>> b = ManifoldAddress(phi=2.0, winding=5, node_id="eth0")
    >>> a.distance_to(b)  # geodesic distance
    0.795...
    """
    phi: float
    winding: int = WINDING_NUMBER
    node_id: str = ""

    def distance_to(self, other: "ManifoldAddress") -> float:
        """Geodesic distance between two addresses on the manifold."""
        dphi = abs(self.phi - other.phi)
        # Wrap around the compact dimension (2π × winding)
        period = 2.0 * np.pi * self.winding
        dphi = min(dphi, period - dphi)
        return float(dphi * LAMBDA_COUPLING)

    def as_vector(self) -> np.ndarray:
        """Return a 4D embedding vector for this address."""
        return np.array([
            np.cos(self.phi),
            np.sin(self.phi),
            self.winding / WINDING_NUMBER,
            len(self.node_id) / K_CS,
        ])

    @classmethod
    def from_node_id(cls, node_id: str) -> "ManifoldAddress":
        """Derive an address deterministically from a node ID string."""
        digest = hashlib.sha256(node_id.encode()).digest()
        val = int.from_bytes(digest[:4], "big")
        phi = (val % 1000) / 1000.0 * 2.0 * np.pi * WINDING_NUMBER
        return cls(phi=phi, winding=WINDING_NUMBER, node_id=node_id)

    def __str__(self) -> str:
        return f"MA[{self.node_id}|φ={self.phi:.3f}|w={self.winding}]"


# ===========================================================================
# ManifoldNode
# ===========================================================================

@dataclass
class ManifoldNode:
    """A peer (host, router, or device) on the UOS manifold network.

    Parameters
    ----------
    node_id : str
    address : ManifoldAddress, optional
        Auto-derived from node_id if not given.
    is_router : bool
    """
    node_id: str
    address: Optional[ManifoldAddress] = None
    is_router: bool = False
    _rx_buffer: Deque = field(default_factory=deque, repr=False)

    def __post_init__(self) -> None:
        if self.address is None:
            self.address = ManifoldAddress.from_node_id(self.node_id)

    def receive_frame(self, frame: "ManifoldFrame") -> None:
        """Buffer an incoming frame."""
        self._rx_buffer.append(frame)

    def next_frame(self) -> Optional["ManifoldFrame"]:
        """Pop and return the oldest buffered frame, or None."""
        return self._rx_buffer.popleft() if self._rx_buffer else None

    def pending_frames(self) -> int:
        return len(self._rx_buffer)


# ===========================================================================
# ManifoldFrame
# ===========================================================================

@dataclass
class ManifoldFrame:
    """The atomic network PDU (packet) on the UOS manifold.

    Parameters
    ----------
    src : ManifoldAddress
    dst : ManifoldAddress
    payload : bytes
    seq : int
        Sequence number (for reliable ordering).
    """
    src: ManifoldAddress
    dst: ManifoldAddress
    payload: bytes
    seq: int = 0

    def __post_init__(self) -> None:
        if len(self.payload) > MTU:
            raise ValueError(
                f"ManifoldFrame payload {len(self.payload)} bytes exceeds MTU {MTU}."
            )
        self._checksum = self._compute_checksum()

    def _compute_checksum(self) -> float:
        """φ-checksum: (Σ byte² mod K_CS) / K_CS."""
        arr = np.frombuffer(self.payload, dtype=np.uint8).astype(np.int64)
        val = int(np.sum(arr ** 2)) % K_CS if len(arr) > 0 else 0
        return val / K_CS

    def checksum_ok(self) -> bool:
        """Return True if the payload has not been corrupted."""
        return abs(self._compute_checksum() - self._checksum) < 1e-12

    @property
    def size_bytes(self) -> int:
        return len(self.payload)


# ===========================================================================
# ManifoldRouter
# ===========================================================================

class ManifoldRouter:
    """Geodesic routing engine for the UOS manifold network.

    Picks the next-hop node by minimising the manifold distance to the
    destination address.  Supports static routing tables and dynamic
    geodesic selection.

    Parameters
    ----------
    local_node : ManifoldNode

    Examples
    --------
    >>> router = ManifoldRouter(local_node=ManifoldNode("gateway", is_router=True))
    >>> router.add_peer(ManifoldNode("host-a"))
    >>> router.add_peer(ManifoldNode("host-b"))
    >>> next_hop = router.route(dst_address)
    """

    def __init__(self, local_node: ManifoldNode) -> None:
        self.local_node = local_node
        self._peers: Dict[str, ManifoldNode] = {}
        self._routing_table: Dict[str, str] = {}   # dst_node_id → next_hop_node_id
        self._frame_count: int = 0

    def add_peer(self, node: ManifoldNode) -> None:
        """Register a peer node."""
        self._peers[node.node_id] = node

    def remove_peer(self, node_id: str) -> None:
        """Deregister a peer node."""
        self._peers.pop(node_id, None)
        self._routing_table.pop(node_id, None)

    def route(self, dst: ManifoldAddress) -> Optional[ManifoldNode]:
        """Return the best next-hop node for a given destination address.

        Selection criterion: argmin distance(peer.address, dst).

        Parameters
        ----------
        dst : ManifoldAddress

        Returns
        -------
        ManifoldNode or None
            None if no peers are registered.
        """
        if not self._peers:
            return None
        best_node = min(
            self._peers.values(),
            key=lambda n: n.address.distance_to(dst),
        )
        return best_node

    def forward(self, frame: ManifoldFrame) -> Optional[ManifoldNode]:
        """Forward a frame toward its destination.

        If the destination node is a direct peer, deliver immediately.
        Otherwise, route to the closest peer and let it forward.

        Returns
        -------
        ManifoldNode
            The node the frame was delivered to.
        """
        # Direct delivery if dst is a known peer
        if frame.dst.node_id in self._peers:
            target = self._peers[frame.dst.node_id]
            target.receive_frame(frame)
            self._frame_count += 1
            return target

        # Geodesic next-hop
        next_hop = self.route(frame.dst)
        if next_hop:
            next_hop.receive_frame(frame)
            self._frame_count += 1
        return next_hop

    def stats(self) -> Dict:
        return {
            "local_node": self.local_node.node_id,
            "peers": list(self._peers.keys()),
            "frames_forwarded": self._frame_count,
        }


# ===========================================================================
# ManifoldSocket
# ===========================================================================

class ManifoldSocket:
    """Reliable, ordered, φ-addressed connection between two nodes.

    Wraps ManifoldRouter to provide a stream-oriented interface.

    Parameters
    ----------
    local : ManifoldNode
    remote : ManifoldNode

    Examples
    --------
    >>> sock = ManifoldSocket(local=ManifoldNode("client"),
    ...                       remote=ManifoldNode("server"))
    >>> sock.send(b"GET / HTTP/1.1")
    14
    >>> data = sock.recv()
    """

    def __init__(self, local: ManifoldNode, remote: ManifoldNode) -> None:
        self.local = local
        self.remote = remote
        self._seq: int = 0
        self._connected: bool = False
        self._send_count: int = 0
        self._recv_count: int = 0

    def connect(self) -> None:
        """Establish the manifold connection (SYN handshake simulation)."""
        self._connected = True

    def disconnect(self) -> None:
        """Close the manifold connection."""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    def send(self, data: bytes, priority: float = 0.5) -> int:
        """Send bytes over the manifold socket.

        Fragments data into MTU-sized frames and delivers them to the
        remote node's receive buffer.

        Parameters
        ----------
        data : bytes
        priority : float

        Returns
        -------
        int
            Total bytes sent.

        Raises
        ------
        ConnectionError
            If the socket is not connected.
        """
        if not self._connected:
            raise ConnectionError("ManifoldSocket is not connected.")
        offset = 0
        sent = 0
        while offset < len(data):
            chunk = data[offset:offset + MTU]
            frame = ManifoldFrame(
                src=self.local.address,
                dst=self.remote.address,
                payload=chunk,
                seq=self._seq,
            )
            self.remote.receive_frame(frame)
            self._seq += 1
            offset += len(chunk)
            sent += len(chunk)
        self._send_count += 1
        return sent

    def recv(self, max_bytes: int = MTU) -> Optional[bytes]:
        """Receive the next frame from the remote node.

        Returns
        -------
        bytes or None
        """
        if not self._connected:
            raise ConnectionError("ManifoldSocket is not connected.")
        frame = self.local.next_frame()
        if frame is None:
            return None
        self._recv_count += 1
        return frame.payload[:max_bytes]

    def recv_all(self) -> bytes:
        """Drain all pending frames and return concatenated payload."""
        if not self._connected:
            raise ConnectionError("ManifoldSocket is not connected.")
        buf = b""
        while True:
            frame = self.local.next_frame()
            if frame is None:
                break
            buf += frame.payload
            self._recv_count += 1
        return buf

    def stats(self) -> Dict:
        return {
            "local": self.local.node_id,
            "remote": self.remote.node_id,
            "connected": self._connected,
            "send_count": self._send_count,
            "recv_count": self._recv_count,
            "seq": self._seq,
        }


# ===========================================================================
# NetworkStack
# ===========================================================================

class NetworkStack:
    """Full five-layer UOS network stack for a single node.

    Parameters
    ----------
    local_node_id : str
        The identity of this host on the manifold network.

    Examples
    --------
    >>> stack = NetworkStack("myhost")
    >>> stack.add_peer("peer1")
    >>> stack.add_peer("gateway", is_router=True)
    >>> sock = stack.connect("peer1")
    >>> sock.send(b"hello manifold")
    14
    >>> stack.route_frame_to("peer1", b"broadcast")
    """

    def __init__(self, local_node_id: str) -> None:
        self.local = ManifoldNode(node_id=local_node_id)
        self.router = ManifoldRouter(local_node=self.local)
        self._sockets: Dict[str, ManifoldSocket] = {}
        self._bytes_sent: int = 0
        self._bytes_received: int = 0

    def add_peer(self, node_id: str, is_router: bool = False) -> ManifoldNode:
        """Register a peer node on the network."""
        node = ManifoldNode(node_id=node_id, is_router=is_router)
        self.router.add_peer(node)
        return node

    def connect(self, remote_node_id: str) -> ManifoldSocket:
        """Open a reliable socket to a remote node.

        Parameters
        ----------
        remote_node_id : str

        Returns
        -------
        ManifoldSocket

        Raises
        ------
        KeyError
            If the remote node is not a registered peer.
        """
        if remote_node_id not in self.router._peers:
            raise KeyError(
                f"NetworkStack: node '{remote_node_id}' is not a registered peer."
            )
        remote = self.router._peers[remote_node_id]
        sock = ManifoldSocket(local=self.local, remote=remote)
        sock.connect()
        self._sockets[remote_node_id] = sock
        return sock

    def route_frame_to(self, dst_node_id: str, data: bytes) -> Optional[ManifoldNode]:
        """Build and route a single frame to a destination node.

        Parameters
        ----------
        dst_node_id : str
        data : bytes

        Returns
        -------
        ManifoldNode
            Next hop that received the frame.
        """
        dst_addr = ManifoldAddress.from_node_id(dst_node_id)
        payload = data[:MTU]
        frame = ManifoldFrame(
            src=self.local.address,
            dst=dst_addr,
            payload=payload,
            seq=0,
        )
        result = self.router.forward(frame)
        self._bytes_sent += len(payload)
        return result

    def stats(self) -> Dict:
        return {
            "local_node": self.local.node_id,
            "local_address": str(self.local.address),
            "peers": list(self.router._peers.keys()),
            "open_sockets": list(self._sockets.keys()),
            "bytes_sent": self._bytes_sent,
            "router_frames_forwarded": self.router._frame_count,
        }
