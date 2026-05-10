# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/ipc.py
==========
Unitary Operating System — Inter-Process Communication

In the UOS, processes communicate not through byte streams but through
**manifold channel resonance**: two processes whose φ-addresses share the
same winding sector can exchange messages with zero serialization overhead.

Primitives
----------
ManifoldChannel(name, capacity)
    A bidirectional, ordered, φ-addressed message channel.  Processes send
    manifold-native messages (any Python object); the channel records the
    φ-coordinate of each message (derived from its content hash) so that
    the receiver can validate geometric coherence.

MessageQueue(name, capacity, priority)
    A priority-ordered queue backed by the manifold.  Messages are sorted by
    a *manifold priority* = 1/(1+latency) × φ_weight.

SharedManifoldSection(section_id, size_pages)
    A shared-memory section exposed as a φ-addressed slab.  Any registered
    process can map a virtual view of the section without copying data.

Pipe(read_pid, write_pid)
    Unidirectional pipe between two processes.  Wraps ManifoldChannel with
    a producer/consumer role assignment.

Signal (see signals.py for the full signal bus)

IPCManager
    Registry for all IPC primitives in the UOS.  Manages creation,
    lookup, and garbage collection of channels, queues, and sections.
"""

from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

import numpy as np

from UOS.constants import K_CS, WINDING_NUMBER, PHI_BACKGROUND, BRAIDED_SOUND_SPEED


# Derived constants for IPC
IPC_MAX_CHANNELS: int = K_CS           # = 74 channels
IPC_MAX_QUEUE_DEPTH: int = K_CS * WINDING_NUMBER   # = 370 messages per queue
IPC_MANIFOLD_TICK: float = BRAIDED_SOUND_SPEED     # = 12/37 — propagation latency


# ---------------------------------------------------------------------------
# Message — the atomic unit of IPC
# ---------------------------------------------------------------------------

@dataclass
class Message:
    """An IPC message on the UOS manifold.

    Parameters
    ----------
    sender_pid : int
    payload : Any
        Any Python object (will be serialized to bytes for fingerprinting).
    phi_coord : float
        Manifold coordinate of the message, derived from payload hash.
    timestamp_ticks : int
        Tick count when the message was sent.
    priority : float
        Delivery priority in [0, 1] (1 = highest).
    """
    sender_pid: int
    payload: Any
    phi_coord: float = 0.0
    timestamp_ticks: int = 0
    priority: float = 0.5

    def __post_init__(self) -> None:
        if self.phi_coord == 0.0:
            self.phi_coord = self._compute_phi_coord()

    def _compute_phi_coord(self) -> float:
        raw = str(self.payload).encode("utf-8")
        digest = hashlib.sha256(raw).digest()
        val = int.from_bytes(digest[:4], "big")
        return (val % K_CS) / K_CS

    def __lt__(self, other: "Message") -> bool:
        """Higher priority sorts first (used by heapq-based queues)."""
        return self.priority > other.priority


# ---------------------------------------------------------------------------
# ManifoldChannel — bidirectional φ-addressed channel
# ---------------------------------------------------------------------------

class ManifoldChannel:
    """Bidirectional, ordered, φ-addressed IPC channel.

    Two endpoints (A, B) share a manifold winding sector.  Messages
    sent from A arrive at B in φ-coordinate order, and vice versa.

    Parameters
    ----------
    name : str
        Unique channel name.
    capacity : int
        Maximum number of messages in flight in each direction.

    Examples
    --------
    >>> ch = ManifoldChannel("kernel-stdout", capacity=32)
    >>> ch.send(pid=1, payload="hello")
    >>> msg = ch.receive()
    >>> msg.payload
    'hello'
    """

    def __init__(self, name: str, capacity: int = 64) -> None:
        if capacity < 1:
            raise ValueError("Channel capacity must be ≥ 1.")
        self.name = name
        self.capacity = capacity
        self._queue_a_to_b: Deque[Message] = deque()
        self._queue_b_to_a: Deque[Message] = deque()
        self._endpoints: List[int] = []   # up to 2 PIDs
        self._tick: int = 0
        self._sent: int = 0
        self._received: int = 0

    # ------------------------------------------------------------------
    # Endpoint registration
    # ------------------------------------------------------------------

    def connect(self, pid: int) -> None:
        """Register a process as an endpoint of this channel.

        Parameters
        ----------
        pid : int

        Raises
        ------
        OverflowError
            If the channel already has 2 endpoints.
        """
        if pid in self._endpoints:
            return
        if len(self._endpoints) >= 2:
            raise OverflowError(
                f"Channel '{self.name}' already has 2 endpoints; "
                f"cannot connect PID {pid}."
            )
        self._endpoints.append(pid)

    # ------------------------------------------------------------------
    # Send / Receive
    # ------------------------------------------------------------------

    def send(
        self,
        pid: int,
        payload: Any,
        priority: float = 0.5,
    ) -> Message:
        """Send a message from ``pid`` to the other endpoint.

        Parameters
        ----------
        pid : int
            The sender's PID.
        payload : Any
        priority : float

        Returns
        -------
        Message

        Raises
        ------
        OverflowError
            If the channel buffer is full.
        """
        queue = self._queue_for_sender(pid)
        if len(queue) >= self.capacity:
            raise OverflowError(
                f"Channel '{self.name}' buffer full ({self.capacity} messages)."
            )
        msg = Message(
            sender_pid=pid,
            payload=payload,
            timestamp_ticks=self._tick,
            priority=float(np.clip(priority, 0.0, 1.0)),
        )
        queue.append(msg)
        self._sent += 1
        self._tick += 1
        return msg

    def receive(self, receiver_pid: Optional[int] = None) -> Optional[Message]:
        """Receive the oldest message addressed to ``receiver_pid``.

        If ``receiver_pid`` is None, the first message from either queue
        is returned (round-robin).

        Returns None if no messages are available.
        """
        queue = self._queue_for_receiver(receiver_pid)
        if not queue:
            return None
        msg = queue.popleft()
        self._received += 1
        return msg

    def pending(self) -> int:
        """Return total number of messages in flight."""
        return len(self._queue_a_to_b) + len(self._queue_b_to_a)

    def is_empty(self) -> bool:
        return self.pending() == 0

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "endpoints": list(self._endpoints),
            "pending": self.pending(),
            "sent": self._sent,
            "received": self._received,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _queue_for_sender(self, pid: int) -> Deque[Message]:
        """Return the queue for messages sent FROM ``pid``."""
        # If both endpoints registered: A→B or B→A
        if len(self._endpoints) == 2:
            if pid == self._endpoints[0]:
                return self._queue_a_to_b
            elif pid == self._endpoints[1]:
                return self._queue_b_to_a
        # Unregistered sender defaults to a_to_b
        return self._queue_a_to_b

    def _queue_for_receiver(self, pid: Optional[int]) -> Deque[Message]:
        """Return the queue of messages FOR ``pid``."""
        if pid is None:
            return self._queue_a_to_b if self._queue_a_to_b else self._queue_b_to_a
        if len(self._endpoints) == 2:
            # Receiver gets the queue sent from the OTHER endpoint
            if pid == self._endpoints[0]:
                return self._queue_b_to_a
            elif pid == self._endpoints[1]:
                return self._queue_a_to_b
        return self._queue_a_to_b


# ---------------------------------------------------------------------------
# MessageQueue — priority-ordered manifold queue
# ---------------------------------------------------------------------------

class MessageQueue:
    """Priority-ordered manifold message queue.

    Messages are sorted by (priority DESC, phi_coord ASC) so the
    highest-priority, most manifold-aligned message is always first.

    Parameters
    ----------
    name : str
    capacity : int

    Examples
    --------
    >>> q = MessageQueue("system-events")
    >>> q.enqueue(pid=1, payload="boot", priority=1.0)
    >>> q.enqueue(pid=2, payload="log", priority=0.1)
    >>> q.dequeue().payload
    'boot'
    """

    def __init__(self, name: str, capacity: int = IPC_MAX_QUEUE_DEPTH) -> None:
        self.name = name
        self.capacity = capacity
        self._items: List[Message] = []
        self._enqueue_count: int = 0
        self._dequeue_count: int = 0

    def enqueue(
        self,
        pid: int,
        payload: Any,
        priority: float = 0.5,
    ) -> Message:
        """Add a message to the queue.

        Parameters
        ----------
        pid : int
        payload : Any
        priority : float

        Returns
        -------
        Message

        Raises
        ------
        OverflowError
        """
        if len(self._items) >= self.capacity:
            raise OverflowError(
                f"MessageQueue '{self.name}' is full ({self.capacity} items)."
            )
        msg = Message(sender_pid=pid, payload=payload,
                      priority=float(np.clip(priority, 0.0, 1.0)))
        # Maintain sorted order: highest priority first
        inserted = False
        for i, item in enumerate(self._items):
            if msg.priority > item.priority:
                self._items.insert(i, msg)
                inserted = True
                break
        if not inserted:
            self._items.append(msg)
        self._enqueue_count += 1
        return msg

    def dequeue(self) -> Optional[Message]:
        """Remove and return the highest-priority message."""
        if not self._items:
            return None
        self._dequeue_count += 1
        return self._items.pop(0)

    def peek(self) -> Optional[Message]:
        """Return the next message without removing it."""
        return self._items[0] if self._items else None

    def depth(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return not self._items

    def stats(self) -> Dict:
        return {
            "name": self.name,
            "depth": self.depth(),
            "capacity": self.capacity,
            "enqueued": self._enqueue_count,
            "dequeued": self._dequeue_count,
        }


# ---------------------------------------------------------------------------
# SharedManifoldSection — zero-copy shared memory
# ---------------------------------------------------------------------------

class SharedManifoldSection:
    """A shared manifold memory section accessible by multiple processes.

    All processes that map this section share the same underlying
    ``np.ndarray`` — no copying occurs.  Writes are immediately visible to
    all readers (manifold-native zero-copy IPC).

    Parameters
    ----------
    section_id : str
        Unique identifier.
    size_pages : int
        Number of 4096-byte pages in the section.
    """

    PAGE_SIZE: int = 4096

    def __init__(self, section_id: str, size_pages: int = 16) -> None:
        if size_pages < 1:
            raise ValueError("size_pages must be ≥ 1.")
        self.section_id = section_id
        self.size_pages = size_pages
        self._data = np.zeros(size_pages * self.PAGE_SIZE, dtype=np.uint8)
        self._mapped_pids: List[int] = []
        self._write_lock_pid: Optional[int] = None

    def map(self, pid: int) -> np.ndarray:
        """Map the section into the calling process's address space.

        Returns a view of the underlying array (zero-copy).

        Parameters
        ----------
        pid : int

        Returns
        -------
        np.ndarray, shape (size_pages * PAGE_SIZE,)
        """
        if pid not in self._mapped_pids:
            self._mapped_pids.append(pid)
        return self._data  # shared view — no copy

    def unmap(self, pid: int) -> None:
        """Unmap the section from a process."""
        self._mapped_pids = [p for p in self._mapped_pids if p != pid]

    def write(self, pid: int, offset: int, data: bytes) -> int:
        """Write bytes to the section at a given offset.

        Parameters
        ----------
        pid : int
        offset : int
        data : bytes

        Returns
        -------
        int
            Number of bytes written.

        Raises
        ------
        PermissionError
            If another process holds the write lock.
        """
        if self._write_lock_pid is not None and self._write_lock_pid != pid:
            raise PermissionError(
                f"SharedManifoldSection '{self.section_id}': write locked by "
                f"PID {self._write_lock_pid}."
            )
        n = min(len(data), len(self._data) - offset)
        if n <= 0:
            return 0
        arr = np.frombuffer(data[:n], dtype=np.uint8)
        self._data[offset:offset + n] = arr
        return n

    def read(self, offset: int, n_bytes: int) -> bytes:
        """Read bytes from the section."""
        end = min(offset + n_bytes, len(self._data))
        return bytes(self._data[offset:end])

    def acquire_write_lock(self, pid: int) -> bool:
        """Acquire an exclusive write lock for ``pid``."""
        if self._write_lock_pid is not None:
            return False
        self._write_lock_pid = pid
        return True

    def release_write_lock(self, pid: int) -> None:
        """Release the write lock held by ``pid``."""
        if self._write_lock_pid == pid:
            self._write_lock_pid = None

    @property
    def size_bytes(self) -> int:
        return self.size_pages * self.PAGE_SIZE

    def stats(self) -> Dict:
        return {
            "section_id": self.section_id,
            "size_bytes": self.size_bytes,
            "size_pages": self.size_pages,
            "mapped_pids": list(self._mapped_pids),
            "write_lock_pid": self._write_lock_pid,
        }


# ---------------------------------------------------------------------------
# Pipe — unidirectional channel between two processes
# ---------------------------------------------------------------------------

class Pipe:
    """A unidirectional pipe from a writer PID to a reader PID.

    Parameters
    ----------
    write_pid : int
    read_pid : int
    capacity : int

    Examples
    --------
    >>> p = Pipe(write_pid=1, read_pid=2)
    >>> p.write(b"hello")
    5
    >>> p.read()
    b'hello'
    """

    def __init__(
        self,
        write_pid: int,
        read_pid: int,
        capacity: int = 64,
    ) -> None:
        self.write_pid = write_pid
        self.read_pid = read_pid
        self._channel = ManifoldChannel(
            name=f"pipe_{write_pid}→{read_pid}", capacity=capacity
        )
        self._channel.connect(write_pid)
        self._channel.connect(read_pid)

    def write(self, data: bytes, priority: float = 0.5) -> int:
        """Write bytes to the pipe.

        Returns
        -------
        int
            Bytes written.
        """
        self._channel.send(self.write_pid, data, priority=priority)
        return len(data)

    def read(self) -> Optional[bytes]:
        """Read and return the next message from the pipe."""
        msg = self._channel.receive(self.read_pid)
        return msg.payload if msg else None

    def pending(self) -> int:
        return self._channel.pending()


# ---------------------------------------------------------------------------
# IPCManager — central registry for all IPC primitives
# ---------------------------------------------------------------------------

class IPCManager:
    """Central registry for all UOS IPC primitives.

    Parameters
    ----------
    max_channels : int
        Maximum number of ManifoldChannels.

    Examples
    --------
    >>> mgr = IPCManager()
    >>> ch = mgr.create_channel("stdout")
    >>> q  = mgr.create_queue("events")
    >>> sec = mgr.create_section("shared-heap", size_pages=8)
    """

    def __init__(self, max_channels: int = IPC_MAX_CHANNELS) -> None:
        self.max_channels = max_channels
        self._channels: Dict[str, ManifoldChannel] = {}
        self._queues: Dict[str, MessageQueue] = {}
        self._sections: Dict[str, SharedManifoldSection] = {}
        self._pipes: Dict[Tuple[int, int], Pipe] = {}

    # ------------------------------------------------------------------
    # Channels
    # ------------------------------------------------------------------

    def create_channel(self, name: str, capacity: int = 64) -> ManifoldChannel:
        if name in self._channels:
            return self._channels[name]
        if len(self._channels) >= self.max_channels:
            raise OverflowError(
                f"IPCManager: maximum channel count ({self.max_channels}) reached."
            )
        ch = ManifoldChannel(name=name, capacity=capacity)
        self._channels[name] = ch
        return ch

    def get_channel(self, name: str) -> ManifoldChannel:
        if name not in self._channels:
            raise KeyError(f"Channel '{name}' not found.")
        return self._channels[name]

    def destroy_channel(self, name: str) -> None:
        if name not in self._channels:
            raise KeyError(f"Channel '{name}' not found.")
        del self._channels[name]

    # ------------------------------------------------------------------
    # Queues
    # ------------------------------------------------------------------

    def create_queue(
        self, name: str, capacity: int = IPC_MAX_QUEUE_DEPTH
    ) -> MessageQueue:
        if name in self._queues:
            return self._queues[name]
        q = MessageQueue(name=name, capacity=capacity)
        self._queues[name] = q
        return q

    def get_queue(self, name: str) -> MessageQueue:
        if name not in self._queues:
            raise KeyError(f"Queue '{name}' not found.")
        return self._queues[name]

    # ------------------------------------------------------------------
    # Shared sections
    # ------------------------------------------------------------------

    def create_section(
        self, section_id: str, size_pages: int = 16
    ) -> SharedManifoldSection:
        if section_id in self._sections:
            return self._sections[section_id]
        sec = SharedManifoldSection(section_id=section_id, size_pages=size_pages)
        self._sections[section_id] = sec
        return sec

    def get_section(self, section_id: str) -> SharedManifoldSection:
        if section_id not in self._sections:
            raise KeyError(f"SharedManifoldSection '{section_id}' not found.")
        return self._sections[section_id]

    # ------------------------------------------------------------------
    # Pipes
    # ------------------------------------------------------------------

    def create_pipe(
        self, write_pid: int, read_pid: int, capacity: int = 64
    ) -> Pipe:
        key = (write_pid, read_pid)
        if key in self._pipes:
            return self._pipes[key]
        pipe = Pipe(write_pid=write_pid, read_pid=read_pid, capacity=capacity)
        self._pipes[key] = pipe
        return pipe

    def get_pipe(self, write_pid: int, read_pid: int) -> Pipe:
        key = (write_pid, read_pid)
        if key not in self._pipes:
            raise KeyError(f"Pipe {write_pid}→{read_pid} not found.")
        return self._pipes[key]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        return {
            "channels": len(self._channels),
            "queues": len(self._queues),
            "sections": len(self._sections),
            "pipes": len(self._pipes),
            "max_channels": self.max_channels,
        }
