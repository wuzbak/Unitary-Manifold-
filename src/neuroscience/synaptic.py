# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/neuroscience/synaptic.py
=============================
Synaptic Transmission as φ-Field Information Transfer — Pillar 20.

Theory
------
A synapse transmits a quantum of φ (a vesicle release event) from the
pre-synaptic terminal to the post-synaptic membrane.  The information
current across the synapse is:

    J_syn = q_φ × release_rate × (1 − saturation)

where q_φ is the quantal φ content of one vesicle and saturation is the
fraction of post-synaptic receptors already bound.  The neurotransmitter
concentration [NT] decays exponentially with time constant τ_NT after
release, modelling re-uptake and diffusion.
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}
import math

_EPS = 1e-30


def synaptic_transmission_phi(q_phi: float, release_rate: float,
                               saturation: float) -> float:
    """Information current across a synapse.

    J_syn = q_φ × release_rate × (1 − saturation)

    Parameters
    ----------
    q_phi        : float — quantal φ per vesicle (must be ≥ 0)
    release_rate : float — vesicle release rate (must be ≥ 0)
    saturation   : float — receptor saturation fraction ∈ [0, 1]

    Returns
    -------
    J_syn : float — synaptic φ-current (≥ 0)
    """
    if q_phi < 0.0:
        raise ValueError(f"q_phi must be ≥ 0, got {q_phi!r}")
    if release_rate < 0.0:
        raise ValueError(f"release_rate must be ≥ 0, got {release_rate!r}")
    if not (0.0 <= saturation <= 1.0):
        raise ValueError(f"saturation must be in [0,1], got {saturation!r}")
    return float(q_phi * release_rate * (1.0 - saturation))


def neurotransmitter_decay(NT_0: float, t: float, tau_NT: float) -> float:
    """Neurotransmitter concentration after time t following release.

    [NT](t) = NT_0 × exp(−t / τ_NT)

    Parameters
    ----------
    NT_0   : float — initial concentration (must be ≥ 0)
    t      : float — time since release (must be ≥ 0)
    tau_NT : float — decay time constant (must be > 0)

    Returns
    -------
    NT : float — concentration at time t
    """
    if NT_0 < 0.0:
        raise ValueError(f"NT_0 must be ≥ 0, got {NT_0!r}")
    if t < 0.0:
        raise ValueError(f"t must be ≥ 0, got {t!r}")
    if tau_NT <= 0.0:
        raise ValueError(f"tau_NT must be > 0, got {tau_NT!r}")
    return float(NT_0 * math.exp(-t / tau_NT))


def receptor_saturation_phi(NT: float, K_d: float) -> float:
    """Fractional receptor occupancy at neurotransmitter concentration NT.

    θ = [NT] / ([NT] + K_d)   (Hill equation, n=1)

    Parameters
    ----------
    NT  : float — neurotransmitter concentration (must be ≥ 0)
    K_d : float — dissociation constant (must be > 0)

    Returns
    -------
    theta : float ∈ [0, 1)
    """
    if NT < 0.0:
        raise ValueError(f"NT must be ≥ 0, got {NT!r}")
    if K_d <= 0.0:
        raise ValueError(f"K_d must be > 0, got {K_d!r}")
    return float(NT / (NT + K_d))


def long_term_potentiation_phi(w_0: float, delta_phi: float, eta: float) -> float:
    """Hebbian long-term potentiation of synaptic weight.

    w_LTP = w_0 + η × Δφ   (Δφ > 0 for co-activation)

    Parameters
    ----------
    w_0      : float — initial weight (must be ≥ 0)
    delta_phi: float — correlated φ-field activation (pre × post)
    eta      : float — learning rate (must be > 0)

    Returns
    -------
    w_LTP : float — potentiated weight (≥ 0)
    """
    if w_0 < 0.0:
        raise ValueError(f"w_0 must be ≥ 0, got {w_0!r}")
    if eta <= 0.0:
        raise ValueError(f"eta must be > 0, got {eta!r}")
    return float(max(0.0, w_0 + eta * delta_phi))


def long_term_depression_phi(w_0: float, depression_rate: float) -> float:
    """Long-term depression: fractional reduction of synaptic weight.

    w_LTD = w_0 × (1 − depression_rate)

    Parameters
    ----------
    w_0             : float — initial weight (must be ≥ 0)
    depression_rate : float — fractional reduction ∈ [0, 1]

    Returns
    -------
    w_LTD : float — depressed weight (≥ 0)
    """
    if w_0 < 0.0:
        raise ValueError(f"w_0 must be ≥ 0, got {w_0!r}")
    if not (0.0 <= depression_rate <= 1.0):
        raise ValueError(f"depression_rate must be in [0,1], got {depression_rate!r}")
    return float(w_0 * (1.0 - depression_rate))


def dopamine_phi_modulation(phi_baseline: float, dopamine_level: float,
                             d1_gain: float = 1.0) -> float:
    """Dopaminergic modulation of synaptic φ-field gain.

    φ_mod = φ_baseline × (1 + d1_gain × dopamine_level)

    Parameters
    ----------
    phi_baseline    : float — baseline φ-field amplitude
    dopamine_level  : float — normalised dopamine concentration ∈ [0, 1]
    d1_gain         : float — D1 receptor gain (default 1.0, must be > 0)

    Returns
    -------
    phi_mod : float — modulated φ amplitude
    """
    if not (0.0 <= dopamine_level <= 1.0):
        raise ValueError(f"dopamine_level must be in [0,1], got {dopamine_level!r}")
    if d1_gain <= 0.0:
        raise ValueError(f"d1_gain must be > 0, got {d1_gain!r}")
    return float(phi_baseline * (1.0 + d1_gain * dopamine_level))


def serotonin_phi(phi_baseline: float, serotonin_level: float,
                  mood_coupling: float = 0.5) -> float:
    """Serotonergic modulation of the emotional φ baseline.

    φ_5HT = φ_baseline × (1 + mood_coupling × (serotonin_level − 0.5))

    Parameters
    ----------
    phi_baseline    : float — resting φ
    serotonin_level : float — normalised serotonin ∈ [0, 1]
    mood_coupling   : float — coupling strength (default 0.5, must be ≥ 0)

    Returns
    -------
    phi_5HT : float — serotonin-modulated φ
    """
    if not (0.0 <= serotonin_level <= 1.0):
        raise ValueError(f"serotonin_level must be in [0,1], got {serotonin_level!r}")
    if mood_coupling < 0.0:
        raise ValueError(f"mood_coupling must be ≥ 0, got {mood_coupling!r}")
    return float(phi_baseline * (1.0 + mood_coupling * (serotonin_level - 0.5)))


def glutamate_snr(J_glu: float, B_noise: float) -> float:
    """Signal-to-noise ratio of glutamatergic excitatory transmission.

    SNR = J_glu / (B_noise + ε)

    Parameters
    ----------
    J_glu   : float — glutamate-driven φ current (must be ≥ 0)
    B_noise : float — synaptic noise floor (must be ≥ 0)

    Returns
    -------
    snr : float — signal-to-noise ratio
    """
    if J_glu < 0.0:
        raise ValueError(f"J_glu must be ≥ 0, got {J_glu!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(J_glu / (B_noise + _EPS))


def gaba_inhibition_phi(phi_pre: float, gaba_fraction: float) -> float:
    """GABAergic inhibition: fraction of pre-synaptic φ suppressed.

    φ_post = φ_pre × (1 − gaba_fraction)

    Parameters
    ----------
    phi_pre      : float — pre-synaptic φ drive (≥ 0)
    gaba_fraction: float — inhibition fraction ∈ [0, 1]

    Returns
    -------
    phi_post : float — residual φ after inhibition
    """
    if phi_pre < 0.0:
        raise ValueError(f"phi_pre must be ≥ 0, got {phi_pre!r}")
    if not (0.0 <= gaba_fraction <= 1.0):
        raise ValueError(f"gaba_fraction must be in [0,1], got {gaba_fraction!r}")
    return float(phi_pre * (1.0 - gaba_fraction))


def synaptic_phi_delay(distance_m: float, v_conduct: float) -> float:
    """Synaptic transmission delay due to axonal conduction.

    delay = distance / v_conduct

    Parameters
    ----------
    distance_m  : float — axon length in metres (must be > 0)
    v_conduct   : float — conduction velocity in m/s (must be > 0)

    Returns
    -------
    delay : float — transmission delay in seconds
    """
    if distance_m <= 0.0:
        raise ValueError(f"distance_m must be > 0, got {distance_m!r}")
    if v_conduct <= 0.0:
        raise ValueError(f"v_conduct must be > 0, got {v_conduct!r}")
    return float(distance_m / v_conduct)
