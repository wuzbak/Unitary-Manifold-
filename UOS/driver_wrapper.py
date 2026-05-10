# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/driver_wrapper.py
=====================
Unitary Operating System — Universal 4D Hardware Wrapper

The UOS kernel speaks 5D manifold geometry; real hardware (x86, ARM, RISC-V,
GPU, NIC, …) speaks 4D linear register/memory instructions.  The
**DriverWrapper** acts as the universal translator: it accepts a 5D *intent
vector* from the hypervisor and projects it down to a 4D *hardware signal*
that a conventional driver can execute.

The projection is the classical Kaluza–Klein dimensional reduction:

    h_μν = G_μν − G_μ5 G_5ν / G_55   (4D induced metric from 5D parent)

Applied to instruction intent:

    hw_signal[μ] = Σ_ν  intent[ν] × projection_matrix[ν, μ]

where ``projection_matrix`` is derived from the current φ-field (the radion
controls the scale of the compact dimension).

The wrapper also maintains a driver registry: each hardware channel (one of
``UOS_DRIVER_CHANNELS = 74``) is mapped to a device type.  When an intent
arrives, the wrapper picks the lowest-latency channel whose device type
matches the intent's resource class.

Public API
----------
HardwareChannel(channel_id, device_type, phi_scale, latency)
    Descriptor for a hardware channel.

DriverWrapper(n_channels, phi_background)
    Main wrapper.

DriverWrapper.register_device(channel_id, device_type, latency)
    Register a hardware device on a channel.

DriverWrapper.translate(intent_5d, resource_class)
    Translate a 5D intent vector to a 4D hardware signal dict.

DriverWrapper.execute(intent_5d, resource_class)
    Translate and (simulated) dispatch the signal; return result dict.

DriverWrapper.channel_latencies()
    Return a dict mapping channel_id → latency.

DriverWrapper.stats()
    Return wrapper statistics.
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

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from UOS.constants import (
    UOS_DRIVER_CHANNELS,
    WINDING_NUMBER,
    PHI_BACKGROUND,
    LAMBDA_COUPLING,
    K_CS,
)

# Dimension of the 5D intent vector (= WINDING_NUMBER = 5)
INTENT_DIM: int = WINDING_NUMBER
# Dimension of the 4D hardware signal (= WINDING_NUMBER - 1 = 4)
SIGNAL_DIM: int = WINDING_NUMBER - 1

# Supported resource classes
RESOURCE_CLASSES = ("cpu", "memory", "storage", "network", "gpu")


# ---------------------------------------------------------------------------
# HardwareChannel — a registered hardware device channel
# ---------------------------------------------------------------------------

@dataclass
class HardwareChannel:
    """Descriptor for a UOS hardware channel.

    Parameters
    ----------
    channel_id : int
        Unique channel identifier in [0, UOS_DRIVER_CHANNELS).
    device_type : str
        One of ``RESOURCE_CLASSES`` ('cpu', 'memory', 'storage', 'network', 'gpu').
    phi_scale : float
        φ-scaling factor for this channel (from the radion field).
    latency : float
        Normalised latency in [0, 1] (0 = zero latency, 1 = maximum latency).
    """
    channel_id: int
    device_type: str
    phi_scale: float = PHI_BACKGROUND
    latency: float = 0.1

    def __post_init__(self) -> None:
        if self.device_type not in RESOURCE_CLASSES:
            raise ValueError(
                f"device_type must be one of {RESOURCE_CLASSES}; got '{self.device_type}'."
            )
        self.latency = float(np.clip(self.latency, 0.0, 1.0))


# ---------------------------------------------------------------------------
# DriverWrapper — the 5D → 4D translation layer
# ---------------------------------------------------------------------------

class DriverWrapper:
    """Universal hardware wrapper: translates 5D manifold intents to 4D signals.

    Parameters
    ----------
    n_channels : int
        Total number of hardware channels.  Default: ``UOS_DRIVER_CHANNELS`` (74).
    phi_background : float
        Background radion value; sets the default KK compactification scale.

    Examples
    --------
    >>> dw = DriverWrapper()
    >>> dw.register_device(0, 'cpu', latency=0.05)
    >>> intent = np.array([1.0, 0.5, 0.0, 0.0, 0.0])
    >>> result = dw.execute(intent, 'cpu')
    >>> result['status']
    'dispatched'
    """

    def __init__(
        self,
        n_channels: int = UOS_DRIVER_CHANNELS,
        phi_background: float = PHI_BACKGROUND,
    ) -> None:
        self.n_channels = n_channels
        self.phi_background = phi_background

        self._channels: Dict[int, HardwareChannel] = {}
        self._dispatch_count: int = 0
        self._total_latency: float = 0.0

    # ------------------------------------------------------------------
    # Device registration
    # ------------------------------------------------------------------

    def register_device(
        self,
        channel_id: int,
        device_type: str,
        latency: float = 0.1,
        phi_scale: float = PHI_BACKGROUND,
    ) -> HardwareChannel:
        """Register a hardware device on a channel.

        Parameters
        ----------
        channel_id : int
            Channel index in [0, n_channels).
        device_type : str
        latency : float
        phi_scale : float

        Returns
        -------
        HardwareChannel
        """
        if not 0 <= channel_id < self.n_channels:
            raise ValueError(
                f"channel_id must be in [0, {self.n_channels}); got {channel_id}."
            )
        ch = HardwareChannel(
            channel_id=channel_id,
            device_type=device_type,
            phi_scale=phi_scale,
            latency=latency,
        )
        self._channels[channel_id] = ch
        return ch

    # ------------------------------------------------------------------
    # Translation: 5D intent → 4D hardware signal
    # ------------------------------------------------------------------

    def translate(
        self, intent_5d: np.ndarray, resource_class: str
    ) -> Dict:
        """Translate a 5D intent vector to a 4D hardware signal.

        The KK reduction projects out the 5th (compact) dimension:

            signal[μ] = φ_scale × Σ_ν  intent[ν] × P[ν, μ]

        where P is the (INTENT_DIM × SIGNAL_DIM) Kaluza–Klein projection
        matrix built from the registered channel's φ-scale.

        Parameters
        ----------
        intent_5d : ndarray, shape (5,)
            5D intent vector.
        resource_class : str
            Target resource class ('cpu', 'memory', 'storage', 'network', 'gpu').

        Returns
        -------
        dict with keys:
            signal_4d : ndarray, shape (4,)
            channel_id : int
            resource_class : str
            phi_scale : float
        """
        if resource_class not in RESOURCE_CLASSES:
            raise ValueError(
                f"resource_class must be one of {RESOURCE_CLASSES}; "
                f"got '{resource_class}'."
            )

        intent = np.asarray(intent_5d, dtype=float)
        if intent.shape != (INTENT_DIM,):
            intent = np.resize(intent, INTENT_DIM)

        # Select the lowest-latency registered channel matching the resource class
        channel = self._select_channel(resource_class)
        phi_scale = channel.phi_scale if channel else self.phi_background

        # Build the KK projection matrix (5 × 4)
        P = self._kk_projection_matrix(phi_scale)
        signal_4d = phi_scale * (P.T @ intent)

        return {
            "signal_4d": signal_4d,
            "channel_id": channel.channel_id if channel else -1,
            "resource_class": resource_class,
            "phi_scale": phi_scale,
        }

    # ------------------------------------------------------------------
    # Execute (simulated dispatch)
    # ------------------------------------------------------------------

    def execute(
        self, intent_5d: np.ndarray, resource_class: str
    ) -> Dict:
        """Translate and dispatch a 5D intent as a simulated hardware call.

        Parameters
        ----------
        intent_5d : ndarray, shape (5,)
        resource_class : str

        Returns
        -------
        dict with keys:
            status : str  ('dispatched' or 'no_channel')
            signal_4d : ndarray, shape (4,)
            channel_id : int
            latency : float
            dispatch_count : int
        """
        translation = self.translate(intent_5d, resource_class)
        channel = self._channels.get(translation["channel_id"])
        latency = channel.latency if channel else 1.0

        self._dispatch_count += 1
        self._total_latency += latency

        status = "dispatched" if translation["channel_id"] >= 0 else "no_channel"
        return {
            "status": status,
            "signal_4d": translation["signal_4d"],
            "channel_id": translation["channel_id"],
            "latency": latency,
            "dispatch_count": self._dispatch_count,
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def channel_latencies(self) -> Dict[int, float]:
        """Return a dict mapping channel_id → latency."""
        return {cid: ch.latency for cid, ch in self._channels.items()}

    def stats(self) -> Dict:
        """Return wrapper statistics."""
        avg_latency = (
            self._total_latency / self._dispatch_count
            if self._dispatch_count > 0 else 0.0
        )
        by_type: Dict[str, int] = {rc: 0 for rc in RESOURCE_CLASSES}
        for ch in self._channels.values():
            by_type[ch.device_type] += 1
        return {
            "registered_channels": len(self._channels),
            "total_channels": self.n_channels,
            "dispatch_count": self._dispatch_count,
            "average_latency": avg_latency,
            "channels_by_type": by_type,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _select_channel(self, resource_class: str) -> Optional[HardwareChannel]:
        """Return the lowest-latency registered channel for ``resource_class``."""
        candidates = [
            ch for ch in self._channels.values() if ch.device_type == resource_class
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda c: c.latency)

    @staticmethod
    def _kk_projection_matrix(phi_scale: float) -> np.ndarray:
        """Build the (INTENT_DIM × SIGNAL_DIM) KK projection matrix.

        The 5th row encodes the compact-dimension coupling:
            P[μ, ν] = δ_{μν}  for μ, ν < 4
            P[4, ν] = λ × φ   for ν < 4  (KK off-diagonal)

        Shape: (5, 4).
        """
        P = np.eye(INTENT_DIM, SIGNAL_DIM)           # (5, 4) identity block
        P[SIGNAL_DIM, :] = LAMBDA_COUPLING * phi_scale  # 5th row: KK coupling
        return P
