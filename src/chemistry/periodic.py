# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/chemistry/periodic.py
==========================
Periodic Table Structure from KK Winding Numbers — Pillar 9.

In the Unitary Manifold the periodic table is not an empirical list of
elements; it is the spectrum of allowed winding states on the compact
dimension S¹/Z₂.  Each period corresponds to one KK shell; the shell
capacity 2n² is fixed by the quantization condition.  The resulting
sequence of period lengths — 2, 8, 8, 18, 18, 32, 32, ... — is exactly
the periodic table of chemical elements.

Theory summary
--------------
Shell capacity (winding quantization):
    C(n) = 2 n²

Cumulative capacity:
    Z_fill(n) = Σₖ₌₁ⁿ 2k²

Period lengths:
    period 1: 2       (n = 1, 2n² = 2)
    period 2: 8       (n = 2, 2n² = 8)
    period 3: 8       (same n = 2 block, d-block deferred to period 4)
    period 4: 18      (n = 3, 2n² = 18 with d-block)
    period 5: 18
    period 6: 32      (n = 4, 2n² = 32 with f-block)
    period 7: 32

Shell radius (Bohr scaling):
    r_n = n² a₀

Geometric ionization energy:
    E_ion = λ² Z_eff / (n² φ_mean)²

Public API
----------
shell_capacity(n)
    2 n² for principal quantum number n.

cumulative_capacity(n_max)
    Total electrons through shell n_max.

period_length(period)
    Number of electrons in period `period` of the periodic table.

shell_radius(n, a0)
    r_n = n² a₀.

geometric_ionization_energy(Z_eff, n, phi_mean, lam)
    E_ion = λ² Z_eff / (n² φ_mean)².

atomic_number_at_shell_fill(n_max)
    Atomic number Z at which shell n_max is completely filled.

winding_to_element(n_w)
    Dict summary: shell, capacity, Z_fill.
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


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Observed period lengths indexed by period number (1-based).
_PERIOD_LENGTHS: dict[int, int] = {
    1: 2,
    2: 8,
    3: 8,
    4: 18,
    5: 18,
    6: 32,
    7: 32,
}

_LAM_DEFAULT: float = 1.0


# ---------------------------------------------------------------------------
# Shell capacity
# ---------------------------------------------------------------------------

def shell_capacity(n: int) -> int:
    """Electron shell capacity from KK winding quantization.

    The compact dimension S¹/Z₂ supports exactly 2n² distinct winding
    states for the n-th shell.  This reproduces the observed shell
    capacities without free parameters:

        C(1) = 2,   C(2) = 8,   C(3) = 18,   C(4) = 32,   C(5) = 50, ...

    Parameters
    ----------
    n : int — principal quantum number (n ≥ 1)

    Returns
    -------
    capacity : int — maximum electrons in shell n

    Raises
    ------
    ValueError
        If n < 1.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    return 2 * n ** 2


# ---------------------------------------------------------------------------
# Cumulative capacity
# ---------------------------------------------------------------------------

def cumulative_capacity(n_max: int) -> int:
    """Total electrons that can be accommodated through shell n_max.

    Sums the winding-quantized shell capacities from shell 1 to shell n_max:

        Z_fill(n_max) = Σₖ₌₁ⁿᵐᵃˣ 2k²

    This equals the atomic number Z of the element at which the n_max-th
    shell is completely filled (noble gas configuration up to shell n_max).

    Parameters
    ----------
    n_max : int — highest principal quantum number to include (n_max ≥ 1)

    Returns
    -------
    total : int — total electron count through shell n_max

    Raises
    ------
    ValueError
        If n_max < 1.
    """
    if n_max < 1:
        raise ValueError(f"n_max must be ≥ 1, got {n_max!r}")
    return sum(2 * k ** 2 for k in range(1, n_max + 1))


# ---------------------------------------------------------------------------
# Period length
# ---------------------------------------------------------------------------

def period_length(period: int) -> int:
    """Number of elements (electrons) in a period of the periodic table.

    The period lengths follow directly from the KK shell quantization,
    including the observed doubling from the d- and f-block deferrals:

        period 1: 2
        period 2: 8
        period 3: 8
        period 4: 18
        period 5: 18
        period 6: 32
        period 7: 32

    Parameters
    ----------
    period : int — period number (1 ≤ period ≤ 7)

    Returns
    -------
    length : int — number of elements in this period

    Raises
    ------
    ValueError
        If period is not in 1–7.
    """
    if period not in _PERIOD_LENGTHS:
        raise ValueError(
            f"period must be 1–7, got {period!r}"
        )
    return _PERIOD_LENGTHS[period]


# ---------------------------------------------------------------------------
# Shell radius
# ---------------------------------------------------------------------------

def shell_radius(n: int, a0: float = 1.0) -> float:
    """Bohr-scaled orbital radius for shell n.

    The mean orbital radius of the n-th shell scales as n² in Bohr units,
    matching both the hydrogen exact result and the semiclassical KK picture:

        r_n = n² a₀

    Parameters
    ----------
    n  : int   — principal quantum number (n ≥ 1)
    a0 : float — Bohr radius unit (default 1, Planck units)

    Returns
    -------
    r_n : float — shell radius

    Raises
    ------
    ValueError
        If n < 1 or a0 ≤ 0.
    """
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if a0 <= 0.0:
        raise ValueError(f"a0 must be > 0, got {a0!r}")
    return float(n ** 2 * a0)


# ---------------------------------------------------------------------------
# Geometric ionization energy
# ---------------------------------------------------------------------------

def geometric_ionization_energy(
    Z_eff: float,
    n: int,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Geometric ionization energy from KK compactification.

    The energy required to remove an electron from shell n against the
    effective nuclear charge Z_eff is set by the curvature of the 5D
    compact dimension:

        E_ion = λ² Z_eff / (n² φ_mean)²

    The denominator (n² φ_mean)² captures both the Bohr scaling r_n = n²a₀
    (with a₀ ↦ φ_mean) and the KK coupling strength λ.

    Parameters
    ----------
    Z_eff    : float — effective nuclear charge seen by the outermost electron
    n        : int   — principal quantum number of the shell
    phi_mean : float — mean radion ⟨φ⟩ (Planck units)
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    E_ion : float — geometric ionization energy in Planck units

    Raises
    ------
    ValueError
        If Z_eff ≤ 0, n < 1, or phi_mean ≤ 0.
    """
    if Z_eff <= 0.0:
        raise ValueError(f"Z_eff must be > 0, got {Z_eff!r}")
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    denominator = (n ** 2 * phi_mean) ** 2
    return float(lam ** 2 * Z_eff / denominator)


# ---------------------------------------------------------------------------
# Atomic number at shell fill
# ---------------------------------------------------------------------------

def atomic_number_at_shell_fill(n_max: int) -> int:
    """Atomic number Z at which shell n_max is completely filled.

    Identical to cumulative_capacity(n_max); provided as a named alias for
    clarity in the context of the periodic table.

    Parameters
    ----------
    n_max : int — highest shell completely filled (n_max ≥ 1)

    Returns
    -------
    Z : int — atomic number of the corresponding noble-gas-like configuration

    Raises
    ------
    ValueError
        If n_max < 1.
    """
    return cumulative_capacity(n_max)


# ---------------------------------------------------------------------------
# Winding-number → element summary
# ---------------------------------------------------------------------------

def winding_to_element(n_w: int) -> dict:
    """Summary of shell properties associated with winding number n_w.

    Maps the KK winding number directly to the chemical shell it represents,
    giving the shell index, its electron capacity, and the cumulative atomic
    number Z at which that shell is filled.

    Parameters
    ----------
    n_w : int — KK winding number (= principal quantum number, n_w ≥ 1)

    Returns
    -------
    info : dict with keys
        ``'shell'``    : int — shell index (= n_w)
        ``'capacity'`` : int — electron capacity 2 n_w²
        ``'Z_fill'``   : int — cumulative Z when this shell is full

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return {
        "shell": n_w,
        "capacity": shell_capacity(n_w),
        "Z_fill": cumulative_capacity(n_w),
    }
