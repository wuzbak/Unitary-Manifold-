# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fh_solver.py
========================
Exact diagonalization (ED) solver for the 1D Fermi–Hubbard model.

EPISTEMIC STATUS — ADJACENT_TRACK_ED_CLOSED
-------------------------------------------
This module is an adjacent research track; it is NOT a hardgate UM pillar
and does not alter the core ToE score.  Results are validated against known
Bethe Ansatz exact solutions for the 2-site half-filling case.

Physical context
----------------
The Jordan–Wigner mapping from fermi_hubbard.py and fermion_mapping.py
converts the second-quantized FH Hamiltonian into a Pauli matrix in the full
2^(2·n_sites) Hilbert space.  Sector decomposition then extracts sub-blocks
with fixed (n_up, n_down) occupation and diagonalises each block independently,
which is exact for any n_sites (memory bounded by 2^(2·n_sites)).

UM-KK natural regime
--------------------
ρ = 2·n₁·n₂ / K_CS = 2·5·7 / 74 = 70/74.
U/t = K_CS² / (2·n₁·n₂) = 74² / 70 ≈ 78.17.
This places the KK-mapped system deep in the Mott insulating phase.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .fermi_hubbard import FermiHubbardHamiltonian, build_fermi_hubbard_1d
from .fermion_mapping import (
    bk_basis_permutations,
    fermion_terms_to_qubit_terms,
    pauli_terms_to_matrix,
)

# ---------------------------------------------------------------------------
# Bethe Ansatz reference data  (2-site, half-filling, 1 up + 1 down)
# E₀ / t = U/(2t) − √[(U/(2t))² + 4]
# ---------------------------------------------------------------------------
BETHE_ANSATZ_2SITE: dict = {
    "U_over_t": [0, 2, 4, 8, 16],
    "E0_over_t": [
        -2.0,
        -1.2360679774997896,
        -0.8284271247461903,
        -0.4721359549995794,
        -0.24621125123532117,
    ],
    "formula": "E0/t = U/(2t) - sqrt((U/(2t))^2 + 4)",
    "description": (
        "2-site half-filling (1 up, 1 down) ground energies from "
        "the exact Bethe Ansatz / 4x4 matrix diagonalisation."
    ),
}


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class FHSectorResult:
    """Exact diagonalization result for a fixed (n_up, n_down) particle sector."""

    n_particles: int
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    ground_energy: float
    first_gap: float  # E[1] − E[0], or 0.0 if the sector has only one state


@dataclass
class FHEdResult:
    """Full exact diagonalization result across all particle sectors."""

    n_sites: int
    hopping_t: float
    interaction_u: float
    ground_energy: float
    first_excited_energy: float
    spectral_gap: float
    charge_gap: float
    spin_gap: float  # −1.0 if not computable (e.g. no adjacent Sz sector)
    ground_state: np.ndarray  # ground eigenvector in its sector basis
    staggered_magnetization: float
    status: str = "ADJACENT_TRACK_ED_SOLVED"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_full_hamiltonian(
    model: FermiHubbardHamiltonian, mapping: str = "jw"
) -> np.ndarray:
    """Return the real Hamiltonian matrix in the full 2^(n_modes) Hilbert space."""
    qubit_terms = fermion_terms_to_qubit_terms(
        model.fermionic_terms(), model.n_modes, mapping=mapping  # type: ignore[arg-type]
    )
    h_complex = pauli_terms_to_matrix(qubit_terms, n_qubits=model.n_modes)
    # Sector slicing below is defined in occupation basis. JW uses occupation
    # ordering directly, while BK terms are generated in BK basis; remap BK
    # back to occupation basis here for consistent sector decomposition.
    if mapping == "bk":
        occ_to_bk, _ = bk_basis_permutations(model.n_modes)
        h_complex = h_complex[np.ix_(occ_to_bk, occ_to_bk)]
    return h_complex.real  # FH Hamiltonian is always real-symmetric


def _sector_indices(model: FermiHubbardHamiltonian, n_up: int, n_down: int) -> np.ndarray:
    """Sorted array of basis-state integers belonging to sector (n_up, n_down).

    Mode indexing follows model.mode_index(site, spin) = 2*site + spin:
      - spin-up  modes: 0, 2, 4, …  (even bit positions)
      - spin-down modes: 1, 3, 5, …  (odd bit positions)
    """
    n_sites = model.n_sites
    indices = []
    for state in range(1 << model.n_modes):
        up_count = sum((state >> (2 * i)) & 1 for i in range(n_sites))
        if up_count != n_up:
            continue
        dn_count = sum((state >> (2 * i + 1)) & 1 for i in range(n_sites))
        if dn_count == n_down:
            indices.append(state)
    return np.array(indices, dtype=np.intp)


def _staggered_mag_expectation(
    model: FermiHubbardHamiltonian,
    gs_vec: np.ndarray,
    indices: np.ndarray,
) -> float:
    """⟨ψ₀|M_stag|ψ₀⟩ where M_stag = (1/L) Σ_i (−1)^i (n_{i↑} − n_{i↓}).

    M_stag is diagonal in the occupation basis, so the expectation value is
    simply Σ_k |ψ₀[k]|² · M_stag(state_k).
    """
    n_sites = model.n_sites
    diag = np.empty(len(indices))
    for k, state in enumerate(indices):
        m = 0.0
        for i in range(n_sites):
            n_up_i = (state >> (2 * i)) & 1
            n_dn_i = (state >> (2 * i + 1)) & 1
            m += ((-1) ** i) * (n_up_i - n_dn_i)
        diag[k] = m / n_sites
    return float(np.dot(np.abs(gs_vec) ** 2, diag))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def solve_sector(
    model: FermiHubbardHamiltonian,
    n_up: int,
    n_down: int,
    mapping: str = "jw",
) -> FHSectorResult:
    """Exact diagonalization of the FH Hamiltonian in the (n_up, n_down) sector.

    Parameters
    ----------
    model:
        FermiHubbardHamiltonian instance (from build_fermi_hubbard_1d).
    n_up:
        Number of spin-up electrons.
    n_down:
        Number of spin-down electrons.
    mapping:
        Fermion-to-qubit mapping; ``"jw"`` (Jordan–Wigner) or ``"bk"``
        (Bravyi–Kitaev, limited to n_modes ≤ 6).

    Returns
    -------
    FHSectorResult
    """
    h_full = _build_full_hamiltonian(model, mapping)
    indices = _sector_indices(model, n_up, n_down)

    if len(indices) == 0:
        return FHSectorResult(
            n_particles=n_up + n_down,
            eigenvalues=np.array([], dtype=float),
            eigenvectors=np.zeros((0, 0), dtype=float),
            ground_energy=np.inf,
            first_gap=0.0,
        )

    h_sector = h_full[np.ix_(indices, indices)]
    eigenvalues, eigenvectors = np.linalg.eigh(h_sector)

    ground_energy = float(eigenvalues[0])
    first_gap = float(eigenvalues[1] - eigenvalues[0]) if len(eigenvalues) > 1 else 0.0

    return FHSectorResult(
        n_particles=n_up + n_down,
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        ground_energy=ground_energy,
        first_gap=first_gap,
    )


def exact_diagonalize(
    model: FermiHubbardHamiltonian, mapping: str = "jw"
) -> FHEdResult:
    """Full exact diagonalization with half-filling as the physical reference.

    Builds the full Hamiltonian matrix once, then extracts and diagonalises
    each sector sub-block.  Works for n_sites = 2, 3, 4 easily; larger
    sizes are functional but slow (exponential in 2·n_sites).

    Half-filling convention
    -----------------------
    The standard Hubbard model is studied at half-filling, where
    N_half = n_sites electrons occupy 2·n_sites modes (one electron per
    site on average).  Without an explicit chemical potential the global
    Hamiltonian minimum may lie at a different filling, so this function
    uses the *half-filled sector minimum* as the reference ground state.
    This matches the physical convention and standard benchmark values
    (Bethe Ansatz, DMRG, QMC).

    Charge gap
    ----------
    Δ_charge = min_{n_up+n_down = N_half+1} E₀(sector)
             + min_{n_up+n_down = N_half−1} E₀(sector)
             − 2 · E_ground(N_half)

    Spin gap
    --------
    Δ_spin = min_{n_up±1, n_down∓1, same N_half} E₀(sector) − E_ground.
    Set to −1.0 if no adjacent-Sz sector is available.
    """
    h_full = _build_full_hamiltonian(model, mapping)

    # --- Solve all sectors ---------------------------------------------------
    sector_data: dict[tuple[int, int], dict] = {}
    for n_up in range(model.n_sites + 1):
        for n_down in range(model.n_sites + 1):
            indices = _sector_indices(model, n_up, n_down)
            if len(indices) == 0:
                continue
            h_sec = h_full[np.ix_(indices, indices)]
            evals, evecs = np.linalg.eigh(h_sec)
            sector_data[(n_up, n_down)] = {
                "eigenvalues": evals,
                "eigenvectors": evecs,
                "indices": indices,
                "ground_energy": float(evals[0]),
            }

    if not sector_data:
        raise RuntimeError("No sectors found — model has no valid Hilbert space.")

    # --- Half-filled ground state (physical reference) -----------------------
    # N_half = n_sites: one electron per site on average.
    N_half = model.n_sites
    half_filled = {k: v for k, v in sector_data.items() if k[0] + k[1] == N_half}
    if not half_filled:
        # Fallback to global minimum if half-filling sectors are absent
        half_filled = sector_data

    gs_key = min(half_filled, key=lambda k: half_filled[k]["ground_energy"])
    gs_data = sector_data[gs_key]
    ground_energy = gs_data["ground_energy"]
    n_up_gs, n_down_gs = gs_key

    # Spectral gap within the ground-state sector
    evals_gs = gs_data["eigenvalues"]
    first_excited_energy = float(evals_gs[1]) if len(evals_gs) > 1 else ground_energy
    spectral_gap = first_excited_energy - ground_energy

    # Ground state vector (in sector basis; column 0 after eigh)
    ground_state = gs_data["eigenvectors"][:, 0].copy()

    # Staggered magnetization
    staggered_mag = _staggered_mag_expectation(model, ground_state, gs_data["indices"])

    # --- Charge gap (relative to half-filling) --------------------------------
    sectors_plus = [v["ground_energy"] for k, v in sector_data.items() if k[0] + k[1] == N_half + 1]
    sectors_minus = [v["ground_energy"] for k, v in sector_data.items() if k[0] + k[1] == N_half - 1]

    if sectors_plus and sectors_minus:
        charge_gap = min(sectors_plus) + min(sectors_minus) - 2.0 * ground_energy
    elif sectors_plus:
        charge_gap = min(sectors_plus) - ground_energy
    elif sectors_minus:
        charge_gap = ground_energy - min(sectors_minus)
    else:
        charge_gap = 0.0

    # --- Spin gap (within N_half, adjacent Sz sectors) ------------------------
    spin_gap: float = -1.0
    for dn_up, dn_dn in ((+1, -1), (-1, +1)):
        candidate = (n_up_gs + dn_up, n_down_gs + dn_dn)
        if (
            candidate in sector_data
            and candidate[0] >= 0
            and candidate[1] >= 0
            and candidate[0] + candidate[1] == N_half
        ):
            spin_gap = sector_data[candidate]["ground_energy"] - ground_energy
            break

    return FHEdResult(
        n_sites=model.n_sites,
        hopping_t=model.hopping_t,
        interaction_u=model.interaction_u,
        ground_energy=ground_energy,
        first_excited_energy=first_excited_energy,
        spectral_gap=spectral_gap,
        charge_gap=charge_gap,
        spin_gap=spin_gap,
        ground_state=ground_state,
        staggered_magnetization=staggered_mag,
        status="ADJACENT_TRACK_ED_SOLVED",
    )


# ---------------------------------------------------------------------------
# Bethe Ansatz validation
# ---------------------------------------------------------------------------


def validate_bethe_ansatz(
    model: FermiHubbardHamiltonian, tol: float = 0.01
) -> dict:
    """Validate ED ground energies against the 2-site Bethe Ansatz.

    Iterates over the reference U/t values in BETHE_ANSATZ_2SITE, builds
    a fresh 2-site model for each, runs exact_diagonalize, and compares
    with the analytic result.  The hopping_t of *model* is used as the
    energy scale.

    Parameters
    ----------
    model:
        Must have n_sites == 2; only model.hopping_t is used.
    tol:
        Absolute tolerance for the energy comparison.

    Returns
    -------
    dict with keys ``max_error``, ``passed``, ``errors_per_U``.
    """
    if model.n_sites != 2:
        raise ValueError(
            "Bethe Ansatz validation is only defined for 2-site models "
            f"(got n_sites={model.n_sites})."
        )

    t = model.hopping_t
    errors: dict[float, float] = {}
    max_error = 0.0

    for u_over_t, e0_over_t in zip(
        BETHE_ANSATZ_2SITE["U_over_t"], BETHE_ANSATZ_2SITE["E0_over_t"]
    ):
        u = u_over_t * t
        test_model = build_fermi_hubbard_1d(n_sites=2, hopping_t=t, interaction_u=u)
        result = exact_diagonalize(test_model)
        expected = e0_over_t * t
        error = abs(result.ground_energy - expected)
        errors[float(u_over_t)] = error
        if error > max_error:
            max_error = error

    return {
        "max_error": max_error,
        "passed": max_error < tol,
        "errors_per_U": errors,
    }


# ---------------------------------------------------------------------------
# UM-KK natural parameters
# ---------------------------------------------------------------------------

_K_CS = 74
_N1 = 5
_N2 = 7


def um_kk_natural_parameters() -> dict:
    """Return the Fermi-Hubbard parameters natural to the UM Kaluza–Klein geometry.

    The (5, 7, 74) braid structure of the Unitary Manifold induces:

        ρ = 2·n₁·n₂ / K_CS = 2·5·7 / 74 = 70/74
        U/t = K_CS² / (2·n₁·n₂) = 74² / 70 ≈ 78.17

    This places the UM system deep in the Mott insulating phase (U/t ≫ 1).
    This is an ADJACENT TRACK connection, not a hardgate physics claim.

    Returns
    -------
    dict with keys: t, U, U_over_t, rho, K_CS, n1, n2, phase, notes.
    """
    rho = (2 * _N1 * _N2) / _K_CS  # 70/74
    U_over_t = (_K_CS ** 2) / (2 * _N1 * _N2)  # 74²/70 ≈ 78.17
    return {
        "t": 1.0,
        "U": U_over_t,  # normalised so that t = 1
        "U_over_t": U_over_t,
        "rho": rho,
        "K_CS": _K_CS,
        "n1": _N1,
        "n2": _N2,
        "phase": "MOTT_INSULATOR",
        "notes": (
            f"KK braid (n1={_N1}, n2={_N2}, K_CS={_K_CS}) maps to Hubbard with "
            f"rho=2*n1*n2/K_CS={rho:.6f}, "
            f"U/t=K_CS^2/(2*n1*n2)={U_over_t:.4f}. "
            "The system is deep in the Mott insulating phase (U/t >> 1). "
            "ADJACENT TRACK — not a hardgate UM claim."
        ),
    }
