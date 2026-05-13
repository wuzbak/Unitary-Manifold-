# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/xdiag_bridge/contract.py
====================================
Canonical model/spec contract for UM ↔ XDiag interoperability.

EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE)
------------------------------------------------------------
This bridge standardizes reproducible data interchange and parity checks.
It is an engineering integration layer and does not alter core physics claims.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
import hashlib
import json

from src.quantum.execution import ExecutionConfig
from src.quantum.fermi_hubbard import FermiHubbardHamiltonian

XDIAG_UM_SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class LatticeSpec:
    n_sites: int
    n_modes: int
    periodic: bool


@dataclass(frozen=True)
class CouplingSpec:
    hopping_t: float
    interaction_u: float
    chemical_potential: float


@dataclass(frozen=True)
class SectorSpec:
    particle_number: int | None = None
    spin_projection: float | None = None


@dataclass(frozen=True)
class ObservableSpec:
    names: tuple[str, ...] = (
        "charge_density",
        "spin_density",
        "double_occupancy",
        "staggered_magnetization",
    )


@dataclass(frozen=True)
class EvolutionSpec:
    total_time: float
    trotter_steps: int
    mapping: str
    backend: str
    shots: int


@dataclass(frozen=True)
class ProvenanceSpec:
    source: str
    generated_at_utc: str
    repository: str
    repo_revision: str = "unknown"
    steward_approval_required: bool = False
    steward_approved: bool = True
    notes: str = ""


@dataclass(frozen=True)
class XDiagBridgeSpec:
    schema_version: str
    integration_lane: str
    lattice: LatticeSpec
    couplings: CouplingSpec
    sector: SectorSpec
    observables: ObservableSpec
    evolution: EvolutionSpec
    provenance: ProvenanceSpec

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def deterministic_run_id(self) -> str:
        payload = self.to_json().encode("utf-8")
        digest = hashlib.sha256(payload).hexdigest()[:12]
        millis = int(self.evolution.total_time * 1000)
        return (
            f"xdiag_{self.lattice.n_sites}s_{self.evolution.mapping}_"
            f"{millis}ms_{self.evolution.trotter_steps}tr_{digest}"
        )



def build_xdiag_bridge_spec(
    model: FermiHubbardHamiltonian,
    config: ExecutionConfig,
    repository: str,
    source: str = "unitary_manifold",
    integration_lane: str = "xdiag_um_bridge_adjacent",
    repo_revision: str = "unknown",
    observables: tuple[str, ...] = (
        "charge_density",
        "spin_density",
        "double_occupancy",
        "staggered_magnetization",
    ),
    particle_number: int | None = None,
    spin_projection: float | None = None,
    steward_approval_required: bool = False,
    steward_approved: bool = True,
    notes: str = "",
) -> XDiagBridgeSpec:
    if config.total_time <= 0:
        raise ValueError("total_time must be positive")
    if config.trotter_steps <= 0:
        raise ValueError("trotter_steps must be positive")

    return XDiagBridgeSpec(
        schema_version=XDIAG_UM_SCHEMA_VERSION,
        integration_lane=integration_lane,
        lattice=LatticeSpec(
            n_sites=model.n_sites,
            n_modes=model.n_modes,
            periodic=model.periodic,
        ),
        couplings=CouplingSpec(
            hopping_t=model.hopping_t,
            interaction_u=model.interaction_u,
            chemical_potential=model.chemical_potential,
        ),
        sector=SectorSpec(
            particle_number=particle_number,
            spin_projection=spin_projection,
        ),
        observables=ObservableSpec(names=observables),
        evolution=EvolutionSpec(
            total_time=config.total_time,
            trotter_steps=config.trotter_steps,
            mapping=config.mapping,
            backend=config.backend,
            shots=config.shots,
        ),
        provenance=ProvenanceSpec(
            source=source,
            generated_at_utc=datetime.now(UTC).isoformat(),
            repository=repository,
            repo_revision=repo_revision,
            steward_approval_required=steward_approval_required,
            steward_approved=steward_approved,
            notes=notes,
        ),
    )



def spec_from_dict(payload: dict[str, object]) -> XDiagBridgeSpec:
    lattice = payload["lattice"]
    couplings = payload["couplings"]
    sector = payload["sector"]
    observables = payload["observables"]
    evolution = payload["evolution"]
    provenance = payload["provenance"]

    if not isinstance(lattice, dict):
        raise ValueError("lattice must be an object")
    if not isinstance(couplings, dict):
        raise ValueError("couplings must be an object")
    if not isinstance(sector, dict):
        raise ValueError("sector must be an object")
    if not isinstance(observables, dict):
        raise ValueError("observables must be an object")
    if not isinstance(evolution, dict):
        raise ValueError("evolution must be an object")
    if not isinstance(provenance, dict):
        raise ValueError("provenance must be an object")

    names_raw = observables.get("names", ())
    names = tuple(names_raw) if isinstance(names_raw, list | tuple) else tuple()

    return XDiagBridgeSpec(
        schema_version=str(payload["schema_version"]),
        integration_lane=str(payload["integration_lane"]),
        lattice=LatticeSpec(
            n_sites=int(lattice["n_sites"]),
            n_modes=int(lattice["n_modes"]),
            periodic=bool(lattice["periodic"]),
        ),
        couplings=CouplingSpec(
            hopping_t=float(couplings["hopping_t"]),
            interaction_u=float(couplings["interaction_u"]),
            chemical_potential=float(couplings["chemical_potential"]),
        ),
        sector=SectorSpec(
            particle_number=int(sector["particle_number"]) if sector.get("particle_number") is not None else None,
            spin_projection=float(sector["spin_projection"]) if sector.get("spin_projection") is not None else None,
        ),
        observables=ObservableSpec(names=names),
        evolution=EvolutionSpec(
            total_time=float(evolution["total_time"]),
            trotter_steps=int(evolution["trotter_steps"]),
            mapping=str(evolution["mapping"]),
            backend=str(evolution["backend"]),
            shots=int(evolution["shots"]),
        ),
        provenance=ProvenanceSpec(
            source=str(provenance["source"]),
            generated_at_utc=str(provenance["generated_at_utc"]),
            repository=str(provenance["repository"]),
            repo_revision=str(provenance.get("repo_revision", "unknown")),
            steward_approval_required=bool(provenance.get("steward_approval_required", False)),
            steward_approved=bool(provenance.get("steward_approved", True)),
            notes=str(provenance.get("notes", "")),
        ),
    )
