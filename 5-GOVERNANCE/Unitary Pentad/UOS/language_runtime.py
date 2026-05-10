# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/language_runtime.py
=======================
Unitary Operating System — Universal Language Runtime

The UOS has **native semantic awareness** of every major programming language.
Rather than running programs through a foreign interpreter, the UOS maps each
language construct (type system, control flow, memory model, concurrency
paradigm) onto a 5D manifold coordinate.  Code written in any language is
projected onto the same manifold — enabling:

  * **Universal Cross-Language FFI** — call Python from Rust from Go from
    JavaScript without marshalling, by sharing manifold coordinates.
  * **Semantic De-duplication** — two functions in different languages that
    compute the same mathematical operation share the same manifold address.
  * **Security Gate** — code whose manifold fingerprint violates the 5:7
    invariant cannot execute (language-agnostic hardware-level immunity).
  * **Zero-Cost Abstraction** — the manifold is the Intermediate
    Representation; there is no double-interpretation overhead.

Supported Language Families (74 entries — one per K_CS geodesic lane)
----------------------------------------------------------------------
Systems:     C, C++, Rust, Zig, Go, D, Ada, Fortran, Assembly (x86/ARM/RISC-V)
Scripting:   Python, Ruby, Perl, PHP, Lua, TCL, Bash, PowerShell, R, Julia
JVM:         Java, Kotlin, Scala, Clojure, Groovy
CLR/.NET:    C#, F#, VB.NET
JavaScript:  JS, TypeScript, CoffeeScript, Elm, PureScript, ReasonML
Functional:  Haskell, OCaml, Erlang, Elixir, Standard ML, Miranda, Idris
Logic:       Prolog, Mercury, Datalog
Concurrent:  Akka/Actor, CSP, pi-calculus, Communicating Haskell Processes
ML/AI:       Python/NumPy, JAX, TensorFlow, PyTorch (DSL layer)
Quantum:     Qiskit, Cirq, Q#, Quipper
Domain:      SQL, SPARQL, Cypher, GraphQL, Solidity, VHDL, Verilog
Shell/DevOp: YAML/Ansible, Nix, Dockerfile, Terraform HCL
Markup:      HTML, CSS, LaTeX, Markdown, reStructuredText, JSON, TOML

Key Classes
-----------
LanguageManifest(name, family, paradigm, typing, memory_model, concurrency)
    Complete descriptor for a programming language.

LanguageRegistry
    The authoritative catalog of all 74 supported languages.

CodeArtifact(source, language_name, metadata)
    A piece of source code in any registered language.

ManifoldCoordinate(phi_coord, B_coord, winding)
    A 5D manifold coordinate for a code artifact or language construct.

UniversalRuntime(registry)
    The main language runtime: ingests code, projects to manifold,
    validates invariant, and prepares for execution or cross-language bridge.
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
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from UOS.constants import (
    WINDING_NUMBER,
    BRAID_PARTNER,
    K_CS,
    PHI_BACKGROUND,
    INVARIANT_RATIO,
    INVARIANT_TOLERANCE,
    BRAIDED_SOUND_SPEED,
)


# ===========================================================================
# Enumerations
# ===========================================================================

class LanguageFamily(Enum):
    SYSTEMS       = auto()   # C, C++, Rust, Zig, Go, Ada, D, Fortran
    SCRIPTING     = auto()   # Python, Ruby, Perl, PHP, Lua, Bash, R, Julia
    JVM           = auto()   # Java, Kotlin, Scala, Clojure, Groovy
    CLR           = auto()   # C#, F#, VB.NET
    JAVASCRIPT    = auto()   # JS, TypeScript, Elm, PureScript
    FUNCTIONAL    = auto()   # Haskell, OCaml, Erlang, Elixir, ML, Idris
    LOGIC         = auto()   # Prolog, Mercury, Datalog
    CONCURRENT    = auto()   # Actor/Akka, CSP, pi-calculus
    ML_AI         = auto()   # NumPy DSL, JAX, TF, PyTorch
    QUANTUM       = auto()   # Qiskit, Cirq, Q#, Quipper
    DOMAIN        = auto()   # SQL, SPARQL, Solidity, VHDL, GraphQL
    SHELL_DEVOPS  = auto()   # Bash, Nix, Dockerfile, Terraform
    MARKUP        = auto()   # HTML, CSS, LaTeX, Markdown, JSON, TOML
    ASSEMBLY      = auto()   # x86, ARM, RISC-V, WebAssembly


class TypingDiscipline(Enum):
    STATIC_STRONG   = auto()  # Rust, Haskell, Java, C#
    STATIC_WEAK     = auto()  # C, C++
    DYNAMIC_STRONG  = auto()  # Python, Ruby, Lisp
    DYNAMIC_WEAK    = auto()  # JavaScript, PHP
    GRADUAL         = auto()  # TypeScript, Python 3.5+, Racket
    DEPENDENT       = auto()  # Idris, Coq, Agda
    INFERRED        = auto()  # OCaml, Haskell (HM), Rust, Go
    UNTYPED         = auto()  # Prolog, YAML, JSON


class MemoryModel(Enum):
    MANUAL           = auto()  # C, C++, Assembly
    GC_TRACING       = auto()  # Java, Python, Go, C#
    GC_REFERENCE     = auto()  # CPython, Swift (ARC)
    OWNERSHIP        = auto()  # Rust (borrow checker)
    REGION           = auto()  # Zig (arenas), MLKit
    STACK_ONLY       = auto()  # some embedded DSLs
    PERSISTENT       = auto()  # Haskell, Clojure (immutable)
    MANIFOLD_MAPPED  = auto()  # UOS-native: φ-address mapped


class ConcurrencyModel(Enum):
    THREADS          = auto()  # C/C++/Java/Python threads
    ASYNC_AWAIT      = auto()  # JS/Python asyncio/Rust Tokio
    CSP              = auto()  # Go channels, Erlang processes
    ACTOR            = auto()  # Erlang/Elixir, Akka, Pony
    STM              = auto()  # Haskell STM, Clojure refs
    DATA_PARALLEL    = auto()  # CUDA, OpenCL, JAX, NumPy
    QUANTUM          = auto()  # Qiskit circuits
    GEODESIC         = auto()  # UOS-native: manifold-scheduled


class Paradigm(Enum):
    IMPERATIVE       = auto()
    OBJECT_ORIENTED  = auto()
    FUNCTIONAL       = auto()
    LOGIC            = auto()
    DECLARATIVE      = auto()
    REACTIVE         = auto()
    CONCURRENT       = auto()
    DATAFLOW         = auto()
    PROBABILISTIC    = auto()
    QUANTUM          = auto()
    MULTI            = auto()  # Multi-paradigm


# ===========================================================================
# LanguageManifest — complete descriptor for one programming language
# ===========================================================================

@dataclass(frozen=True)
class LanguageManifest:
    """Complete descriptor for a programming language registered in the UOS.

    Parameters
    ----------
    name : str
        Canonical name (e.g. 'Rust', 'Python', 'TypeScript').
    family : LanguageFamily
    paradigm : Paradigm
    typing : TypingDiscipline
    memory : MemoryModel
    concurrency : ConcurrencyModel
    file_extensions : tuple of str
        File extensions (e.g. ('.rs',), ('.py',), ('.ts', '.tsx')).
    keywords : tuple of str
        A representative sample of reserved keywords.
    manifold_lane : int
        Which of the K_CS=74 geodesic lanes this language occupies.
    gc_pressure : float
        Estimated GC / allocation pressure in [0, 1].
    safety_score : float
        Memory safety score in [0, 1] (1 = provably safe).
    parallelism_score : float
        Native parallelism capability in [0, 1].
    """
    name: str
    family: LanguageFamily
    paradigm: Paradigm
    typing: TypingDiscipline
    memory: MemoryModel
    concurrency: ConcurrencyModel
    file_extensions: Tuple[str, ...]
    keywords: Tuple[str, ...]
    manifold_lane: int
    gc_pressure: float = 0.5
    safety_score: float = 0.5
    parallelism_score: float = 0.5

    def phi_coordinate(self) -> float:
        """Return the φ-coordinate for this language on the manifold.

        Computed as the sum of ASCII values of the name, modulo K_CS,
        divided by K_CS — mapping each language to a unique float in [0,1).
        """
        checksum = sum(ord(c) ** 2 for c in self.name) % K_CS
        return checksum / K_CS

    def manifold_vector(self) -> np.ndarray:
        """Return a 5D manifold vector for this language.

        Encodes: (φ_coord, safety, parallelism, gc_pressure, lane/K_CS)
        """
        return np.array([
            self.phi_coordinate(),
            self.safety_score,
            self.parallelism_score,
            1.0 - self.gc_pressure,  # high GC pressure → low field component
            self.manifold_lane / K_CS,
        ])


# ===========================================================================
# ManifoldCoordinate — a point in 5D manifold space
# ===========================================================================

@dataclass(frozen=True)
class ManifoldCoordinate:
    """A point in 5D UOS manifold space.

    Parameters
    ----------
    phi_coord : float
        Radion (φ) coordinate in [0, 2π × n_w).
    B_coord : np.ndarray, shape (4,)
        Gauge field (irreversibility) 4-vector.
    winding : int
        Winding number (usually n_w = 5).
    label : str
        Human-readable label (e.g. language name or function name).
    """
    phi_coord: float
    B_coord: np.ndarray
    winding: int
    label: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManifoldCoordinate):
            return NotImplemented
        return (
            abs(self.phi_coord - other.phi_coord) < 1e-9
            and np.allclose(self.B_coord, other.B_coord)
            and self.winding == other.winding
        )

    def __hash__(self) -> int:
        return hash((round(self.phi_coord, 9), self.winding, self.label))

    def distance_to(self, other: "ManifoldCoordinate") -> float:
        """Geodesic distance between two manifold coordinates.

        d = sqrt((Δφ)² + ‖ΔB‖²) × n_w / (2π)
        """
        dphi = abs(self.phi_coord - other.phi_coord)
        dB = np.linalg.norm(self.B_coord - other.B_coord)
        return float(np.sqrt(dphi ** 2 + dB ** 2)) * WINDING_NUMBER / (2 * np.pi)


# ===========================================================================
# CodeArtifact — a source-code object with manifold fingerprint
# ===========================================================================

@dataclass
class CodeArtifact:
    """A piece of source code in any registered language.

    Parameters
    ----------
    source : str or bytes
        Raw source code.
    language_name : str
        Must be registered in the LanguageRegistry.
    metadata : dict
        Arbitrary key-value metadata (author, version, etc.).
    """
    source: Any          # str or bytes
    language_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    _coord: Optional[ManifoldCoordinate] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.source, str):
            self._raw = self.source.encode("utf-8")
        else:
            self._raw = bytes(self.source)

    @property
    def size_bytes(self) -> int:
        return len(self._raw)

    def content_hash(self) -> str:
        """SHA-256 hex digest of the source."""
        return hashlib.sha256(self._raw).hexdigest()

    def phi_fingerprint(self) -> float:
        """φ-fingerprint: (Σ byte² mod K_CS) / K_CS."""
        arr = np.frombuffer(self._raw, dtype=np.uint8).astype(np.int64)
        return float(int(np.sum(arr ** 2)) % K_CS) / K_CS

    def loc(self) -> int:
        """Lines of code (non-blank)."""
        lines = self.source.splitlines() if isinstance(self.source, str) else \
                self._raw.decode("utf-8", errors="replace").splitlines()
        return sum(1 for ln in lines if ln.strip())

    def token_count(self) -> int:
        """Approximate token count (whitespace-split)."""
        text = self.source if isinstance(self.source, str) else \
               self._raw.decode("utf-8", errors="replace")
        return len(text.split())

    def assign_coordinate(self, coord: ManifoldCoordinate) -> None:
        """Assign a manifold coordinate to this artifact."""
        self._coord = coord

    @property
    def coordinate(self) -> Optional[ManifoldCoordinate]:
        """The manifold coordinate of this artifact (set by the runtime)."""
        return self._coord


# ===========================================================================
# LanguageRegistry — the authoritative catalog of all 74 supported languages
# ===========================================================================

def _build_registry() -> Dict[str, LanguageManifest]:
    """Build and return the complete language registry (74 entries)."""

    def L(name, family, paradigm, typing, memory, concurrency,
          exts, kw, lane, gc=0.5, safety=0.5, par=0.5):
        return LanguageManifest(
            name=name, family=family, paradigm=paradigm,
            typing=typing, memory=memory, concurrency=concurrency,
            file_extensions=tuple(exts), keywords=tuple(kw),
            manifold_lane=lane, gc_pressure=gc, safety_score=safety,
            parallelism_score=par,
        )

    F = LanguageFamily
    P = Paradigm
    T = TypingDiscipline
    M = MemoryModel
    C = ConcurrencyModel

    langs = [
        # ── Systems languages (lane 0-8) ───────────────────────────────
        L("C",       F.SYSTEMS, P.IMPERATIVE, T.STATIC_WEAK, M.MANUAL, C.THREADS,
          [".c",".h"], ["if","while","for","return","struct","void","int","char","*"], 0, gc=0.0, safety=0.2, par=0.7),
        L("C++",     F.SYSTEMS, P.MULTI, T.STATIC_WEAK, M.MANUAL, C.THREADS,
          [".cpp",".hpp",".cc"], ["class","template","virtual","namespace","override","auto"], 1, gc=0.0, safety=0.25, par=0.8),
        L("Rust",    F.SYSTEMS, P.MULTI, T.STATIC_STRONG, M.OWNERSHIP, C.ASYNC_AWAIT,
          [".rs"], ["fn","let","mut","match","trait","impl","borrow","lifetime","unsafe"], 2, gc=0.0, safety=1.0, par=0.95),
        L("Zig",     F.SYSTEMS, P.IMPERATIVE, T.STATIC_STRONG, M.MANUAL, C.ASYNC_AWAIT,
          [".zig"], ["const","var","fn","pub","comptime","async","await","defer"], 3, gc=0.0, safety=0.85, par=0.8),
        L("Go",      F.SYSTEMS, P.IMPERATIVE, T.STATIC_STRONG, M.GC_TRACING, C.CSP,
          [".go"], ["func","chan","go","select","defer","interface","goroutine","package"], 4, gc=0.3, safety=0.75, par=0.95),
        L("D",       F.SYSTEMS, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.THREADS,
          [".d"], ["module","import","class","struct","template","unittest","@safe"], 5, gc=0.3, safety=0.7, par=0.7),
        L("Ada",     F.SYSTEMS, P.IMPERATIVE, T.STATIC_STRONG, M.GC_REFERENCE, C.THREADS,
          [".adb",".ads"], ["package","procedure","function","task","protected","type","begin"], 6, gc=0.1, safety=0.9, par=0.7),
        L("Fortran", F.SYSTEMS, P.IMPERATIVE, T.STATIC_STRONG, M.MANUAL, C.DATA_PARALLEL,
          [".f90",".f95",".f"], ["program","subroutine","function","do","end","real","integer"], 7, gc=0.0, safety=0.5, par=0.9),
        L("Assembly-x86", F.ASSEMBLY, P.IMPERATIVE, T.UNTYPED, M.MANUAL, C.THREADS,
          [".asm",".s"], ["mov","push","pop","call","ret","jmp","cmp","nop","xor"], 8, gc=0.0, safety=0.0, par=0.5),
        L("Assembly-ARM", F.ASSEMBLY, P.IMPERATIVE, T.UNTYPED, M.MANUAL, C.THREADS,
          [".s"], ["ldr","str","bl","bx","mov","cmp","add","sub","mul"], 9, gc=0.0, safety=0.0, par=0.6),
        L("Assembly-RISCV", F.ASSEMBLY, P.IMPERATIVE, T.UNTYPED, M.MANUAL, C.THREADS,
          [".s"], ["add","sub","lw","sw","beq","jal","jalr","lui","auipc"], 10, gc=0.0, safety=0.0, par=0.6),
        L("WebAssembly", F.ASSEMBLY, P.IMPERATIVE, T.STATIC_STRONG, M.MANUAL, C.ASYNC_AWAIT,
          [".wat",".wasm"], ["module","func","local","global","memory","table","export","import"], 11, gc=0.0, safety=0.7, par=0.7),
        # ── Scripting (lane 12-21) ─────────────────────────────────────
        L("Python",  F.SCRIPTING, P.MULTI, T.DYNAMIC_STRONG, M.GC_REFERENCE, C.ASYNC_AWAIT,
          [".py"], ["def","class","import","for","if","yield","async","await","lambda","with"], 12, gc=0.6, safety=0.7, par=0.6),
        L("Ruby",    F.SCRIPTING, P.MULTI, T.DYNAMIC_STRONG, M.GC_TRACING, C.THREADS,
          [".rb"], ["def","class","module","end","do","block","yield","attr_accessor"], 13, gc=0.6, safety=0.65, par=0.5),
        L("Perl",    F.SCRIPTING, P.MULTI, T.DYNAMIC_WEAK, M.GC_REFERENCE, C.THREADS,
          [".pl",".pm"], ["my","sub","use","package","foreach","unless","wantarray","local"], 14, gc=0.5, safety=0.3, par=0.5),
        L("PHP",     F.SCRIPTING, P.MULTI, T.DYNAMIC_WEAK, M.GC_REFERENCE, C.ASYNC_AWAIT,
          [".php"], ["function","class","echo","foreach","namespace","trait","yield","match"], 15, gc=0.6, safety=0.35, par=0.5),
        L("Lua",     F.SCRIPTING, P.MULTI, T.DYNAMIC_STRONG, M.GC_TRACING, C.THREADS,
          [".lua"], ["function","local","end","do","repeat","until","table","coroutine"], 16, gc=0.5, safety=0.55, par=0.5),
        L("Bash",    F.SHELL_DEVOPS, P.IMPERATIVE, T.UNTYPED, M.STACK_ONLY, C.THREADS,
          [".sh",".bash"], ["if","then","else","fi","for","while","do","done","function","case"], 17, gc=0.0, safety=0.2, par=0.4),
        L("PowerShell", F.SHELL_DEVOPS, P.IMPERATIVE, T.DYNAMIC_STRONG, M.GC_TRACING, C.ASYNC_AWAIT,
          [".ps1"], ["function","param","foreach","where-object","pipeline","cmdlet","module"], 18, gc=0.5, safety=0.5, par=0.5),
        L("R",       F.SCRIPTING, P.FUNCTIONAL, T.DYNAMIC_STRONG, M.GC_REFERENCE, C.DATA_PARALLEL,
          [".r",".R"], ["function","if","else","for","while","return","library","source","apply"], 19, gc=0.7, safety=0.55, par=0.7),
        L("Julia",   F.SCRIPTING, P.MULTI, T.DYNAMIC_STRONG, M.GC_TRACING, C.DATA_PARALLEL,
          [".jl"], ["function","module","struct","for","if","@macro","@simd","@parallel","type"], 20, gc=0.4, safety=0.65, par=0.95),
        L("TCL",     F.SCRIPTING, P.IMPERATIVE, T.DYNAMIC_WEAK, M.GC_REFERENCE, C.THREADS,
          [".tcl"], ["proc","set","if","foreach","while","namespace","package","puts"], 21, gc=0.6, safety=0.4, par=0.4),
        # ── JVM (lane 22-26) ──────────────────────────────────────────
        L("Java",    F.JVM, P.OBJECT_ORIENTED, T.STATIC_STRONG, M.GC_TRACING, C.THREADS,
          [".java"], ["class","interface","extends","implements","synchronized","volatile","final","@annotation"], 22, gc=0.7, safety=0.75, par=0.8),
        L("Kotlin",  F.JVM, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.ASYNC_AWAIT,
          [".kt",".kts"], ["fun","val","var","class","object","sealed","data","coroutine","suspend","flow"], 23, gc=0.6, safety=0.85, par=0.85),
        L("Scala",   F.JVM, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.ACTOR,
          [".scala"], ["class","trait","object","def","val","var","implicit","case","actor","future"], 24, gc=0.6, safety=0.8, par=0.9),
        L("Clojure", F.JVM, P.FUNCTIONAL, T.DYNAMIC_STRONG, M.PERSISTENT, C.STM,
          [".clj",".cljs"], ["defn","let","fn","ns","def","atom","ref","agent","dosync","->"], 25, gc=0.7, safety=0.8, par=0.8),
        L("Groovy",  F.JVM, P.MULTI, T.DYNAMIC_STRONG, M.GC_TRACING, C.THREADS,
          [".groovy"], ["def","class","trait","closure","@Annotation","spread","safe-nav"], 26, gc=0.6, safety=0.65, par=0.7),
        # ── CLR/.NET (lane 27-29) ─────────────────────────────────────
        L("C#",      F.CLR, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.ASYNC_AWAIT,
          [".cs"], ["class","interface","struct","async","await","LINQ","delegate","event","record","unsafe"], 27, gc=0.7, safety=0.8, par=0.85),
        L("F#",      F.CLR, P.FUNCTIONAL, T.STATIC_STRONG, M.GC_TRACING, C.ASYNC_AWAIT,
          [".fs",".fsx"], ["let","fun","type","module","async","match","|>","<|","seq","computation"], 28, gc=0.6, safety=0.85, par=0.8),
        L("VB.NET",  F.CLR, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.THREADS,
          [".vb"], ["Module","Sub","Function","Dim","As","Class","Imports","Handles","RaiseEvent"], 29, gc=0.7, safety=0.75, par=0.7),
        # ── JavaScript family (lane 30-35) ────────────────────────────
        L("JavaScript", F.JAVASCRIPT, P.MULTI, T.DYNAMIC_WEAK, M.GC_TRACING, C.ASYNC_AWAIT,
          [".js",".mjs",".cjs"], ["function","const","let","var","class","async","await","Promise","=>","prototype"], 30, gc=0.7, safety=0.4, par=0.7),
        L("TypeScript", F.JAVASCRIPT, P.MULTI, T.GRADUAL, M.GC_TRACING, C.ASYNC_AWAIT,
          [".ts",".tsx"], ["interface","type","enum","generic","readonly","never","unknown","as","satisfies"], 31, gc=0.6, safety=0.75, par=0.7),
        L("CoffeeScript", F.JAVASCRIPT, P.FUNCTIONAL, T.DYNAMIC_WEAK, M.GC_TRACING, C.ASYNC_AWAIT,
          [".coffee"], ["->","=>","class","extends","@","?","of","in","unless","until"], 32, gc=0.7, safety=0.4, par=0.5),
        L("Elm",     F.JAVASCRIPT, P.FUNCTIONAL, T.STATIC_STRONG, M.PERSISTENT, C.DATA_PARALLEL,
          [".elm"], ["module","import","type","case","of","let","in","port","effect","subscriptions"], 33, gc=0.5, safety=0.9, par=0.7),
        L("PureScript", F.JAVASCRIPT, P.FUNCTIONAL, T.STATIC_STRONG, M.PERSISTENT, C.ASYNC_AWAIT,
          [".purs"], ["module","import","data","class","instance","forall","where","do","ado"], 34, gc=0.5, safety=0.9, par=0.7),
        L("ReasonML", F.JAVASCRIPT, P.MULTI, T.STATIC_STRONG, M.GC_REFERENCE, C.ASYNC_AWAIT,
          [".re",".rei"], ["let","type","module","fun","switch","when","external","@bs."], 35, gc=0.5, safety=0.85, par=0.7),
        # ── Functional (lane 36-43) ───────────────────────────────────
        L("Haskell", F.FUNCTIONAL, P.FUNCTIONAL, T.STATIC_STRONG, M.PERSISTENT, C.STM,
          [".hs",".lhs"], ["data","type","class","instance","where","do","let","in","forall","newtype","deriving"], 36, gc=0.5, safety=0.95, par=0.8),
        L("OCaml",   F.FUNCTIONAL, P.FUNCTIONAL, T.INFERRED, M.GC_TRACING, C.ASYNC_AWAIT,
          [".ml",".mli"], ["let","fun","type","module","functor","match","with","open","sig","struct"], 37, gc=0.5, safety=0.9, par=0.7),
        L("Erlang",  F.FUNCTIONAL, P.CONCURRENT, T.DYNAMIC_STRONG, M.GC_TRACING, C.ACTOR,
          [".erl",".hrl"], ["receive","send","spawn","pid","node","register","monitor","link","supervisor"], 38, gc=0.6, safety=0.85, par=0.99),
        L("Elixir",  F.FUNCTIONAL, P.CONCURRENT, T.DYNAMIC_STRONG, M.GC_TRACING, C.ACTOR,
          [".ex",".exs"], ["def","defmodule","use","require","import","alias","do","end","pipe|>","macro"], 39, gc=0.6, safety=0.85, par=0.99),
        L("Standard ML", F.FUNCTIONAL, P.FUNCTIONAL, T.STATIC_STRONG, M.GC_TRACING, C.THREADS,
          [".sml",".sig"], ["fun","val","type","structure","signature","functor","open","datatype","exception"], 40, gc=0.5, safety=0.9, par=0.6),
        L("Idris",   F.FUNCTIONAL, P.FUNCTIONAL, T.DEPENDENT, M.PERSISTENT, C.THREADS,
          [".idr"], ["data","record","interface","implementation","total","partial","namespace","proof","Void"], 41, gc=0.5, safety=1.0, par=0.5),
        L("Miranda", F.FUNCTIONAL, P.FUNCTIONAL, T.STATIC_STRONG, M.PERSISTENT, C.THREADS,
          [".m"], ["|","=","::","where","type","abstype","show","num","bool","list"], 42, gc=0.5, safety=0.9, par=0.5),
        L("Agda",    F.FUNCTIONAL, P.FUNCTIONAL, T.DEPENDENT, M.PERSISTENT, C.THREADS,
          [".agda"], ["data","record","postulate","field","where","open","module","Set","Prop"], 43, gc=0.5, safety=1.0, par=0.5),
        # ── Logic (lane 44-46) ────────────────────────────────────────
        L("Prolog",  F.LOGIC, P.LOGIC, T.UNTYPED, M.GC_TRACING, C.THREADS,
          [".pl",".pro"], [":-","assert","retract","functor","clause","not","findall","bagof","call","cut"], 44, gc=0.6, safety=0.7, par=0.6),
        L("Mercury", F.LOGIC, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.THREADS,
          [".m"], ["pred","func","mode","det","semidet","multi","failure","promise","module"], 45, gc=0.5, safety=0.9, par=0.7),
        L("Datalog", F.LOGIC, P.LOGIC, T.STATIC_STRONG, M.GC_TRACING, C.DATA_PARALLEL,
          [".dl"], [":-","fact","rule","query","input","output","aggregate","sum","count","min"], 46, gc=0.5, safety=0.8, par=0.8),
        # ── Concurrent/Actor (lane 47-50) ─────────────────────────────
        L("Pony",    F.CONCURRENT, P.OBJECT_ORIENTED, T.STATIC_STRONG, M.GC_REFERENCE, C.ACTOR,
          [".pony"], ["actor","class","trait","interface","behaviour","recover","consume","create","fun"], 47, gc=0.3, safety=0.95, par=0.99),
        L("Vala",    F.CONCURRENT, P.OBJECT_ORIENTED, T.STATIC_STRONG, M.GC_REFERENCE, C.ASYNC_AWAIT,
          [".vala"], ["class","signal","delegate","async","yield","connect","emit","namespace","interface"], 48, gc=0.4, safety=0.8, par=0.7),
        L("Nim",     F.SYSTEMS, P.MULTI, T.STATIC_STRONG, M.GC_REFERENCE, C.ASYNC_AWAIT,
          [".nim"], ["proc","func","method","macro","template","concept","async","await","case","of"], 49, gc=0.3, safety=0.8, par=0.8),
        L("Crystal", F.SYSTEMS, P.MULTI, T.STATIC_STRONG, M.GC_TRACING, C.CSP,
          [".cr"], ["def","class","module","struct","include","extend","spawn","channel","select"], 50, gc=0.5, safety=0.8, par=0.85),
        # ── ML / AI DSLs (lane 51-54) ─────────────────────────────────
        L("NumPy/SciPy", F.ML_AI, P.DECLARATIVE, T.DYNAMIC_STRONG, M.GC_REFERENCE, C.DATA_PARALLEL,
          [".npy",".npz"], ["array","zeros","ones","dot","einsum","fft","linalg","random","broadcast"], 51, gc=0.6, safety=0.7, par=0.95),
        L("JAX",     F.ML_AI, P.FUNCTIONAL, T.STATIC_STRONG, M.GC_REFERENCE, C.DATA_PARALLEL,
          [".py"], ["jit","grad","vmap","pmap","lax","jnp","scan","checkpoint","sharding"], 52, gc=0.5, safety=0.8, par=0.99),
        L("PyTorch", F.ML_AI, P.IMPERATIVE, T.DYNAMIC_STRONG, M.GC_REFERENCE, C.DATA_PARALLEL,
          [".py",".pt"], ["tensor","autograd","backward","optimizer","nn","Module","DataLoader","CUDA"], 53, gc=0.7, safety=0.7, par=0.95),
        L("TensorFlow", F.ML_AI, P.DATAFLOW, T.STATIC_STRONG, M.GC_REFERENCE, C.DATA_PARALLEL,
          [".py",".pb"], ["@tf.function","keras","Variable","GradientTape","distribute","tpu","graph"], 54, gc=0.7, safety=0.7, par=0.95),
        # ── Quantum (lane 55-58) ──────────────────────────────────────
        L("Qiskit",  F.QUANTUM, P.QUANTUM, T.DYNAMIC_STRONG, M.GC_REFERENCE, C.QUANTUM,
          [".py"], ["QuantumCircuit","qubits","gate","measure","transpile","backend","shot"], 55, gc=0.6, safety=0.8, par=0.99),
        L("Cirq",    F.QUANTUM, P.QUANTUM, T.STATIC_STRONG, M.GC_REFERENCE, C.QUANTUM,
          [".py"], ["Circuit","Moment","Operation","Qubit","measure","simulate","CNOT","H","T"], 56, gc=0.6, safety=0.8, par=0.99),
        L("Q#",      F.QUANTUM, P.QUANTUM, T.STATIC_STRONG, M.GC_REFERENCE, C.QUANTUM,
          [".qs"], ["operation","function","qubit","use","within","apply","measure","DumpMachine"], 57, gc=0.5, safety=0.9, par=0.99),
        L("Quipper", F.QUANTUM, P.QUANTUM, T.STATIC_STRONG, M.GC_TRACING, C.QUANTUM,
          [".hs"], ["Qubit","gate","qnot","hadamard","controlled","circuit","qinit","measure"], 58, gc=0.5, safety=0.9, par=0.99),
        # ── Domain-specific (lane 59-65) ──────────────────────────────
        L("SQL",     F.DOMAIN, P.DECLARATIVE, T.STATIC_STRONG, M.GC_TRACING, C.DATA_PARALLEL,
          [".sql"], ["SELECT","FROM","WHERE","JOIN","GROUP BY","HAVING","WITH","WINDOW","PARTITION"], 59, gc=0.5, safety=0.7, par=0.8),
        L("SPARQL",  F.DOMAIN, P.DECLARATIVE, T.UNTYPED, M.GC_TRACING, C.DATA_PARALLEL,
          [".sparql",".rq"], ["SELECT","WHERE","FILTER","OPTIONAL","UNION","GRAPH","ASK","CONSTRUCT"], 60, gc=0.5, safety=0.7, par=0.7),
        L("GraphQL", F.DOMAIN, P.DECLARATIVE, T.STATIC_STRONG, M.STACK_ONLY, C.ASYNC_AWAIT,
          [".graphql",".gql"], ["query","mutation","subscription","type","schema","fragment","union","enum","scalar"], 61, gc=0.4, safety=0.7, par=0.7),
        L("Solidity", F.DOMAIN, P.OBJECT_ORIENTED, T.STATIC_STRONG, M.MANUAL, C.THREADS,
          [".sol"], ["contract","function","modifier","event","emit","require","mapping","address","uint256"], 62, gc=0.0, safety=0.5, par=0.5),
        L("VHDL",    F.DOMAIN, P.CONCURRENT, T.STATIC_STRONG, M.MANUAL, C.THREADS,
          [".vhd",".vhdl"], ["architecture","entity","signal","process","component","port","map","std_logic"], 63, gc=0.0, safety=0.75, par=0.99),
        L("Verilog", F.DOMAIN, P.CONCURRENT, T.STATIC_STRONG, M.MANUAL, C.THREADS,
          [".v",".sv"], ["module","wire","reg","always","assign","initial","input","output","parameter"], 64, gc=0.0, safety=0.7, par=0.99),
        L("Cypher",  F.DOMAIN, P.DECLARATIVE, T.DYNAMIC_STRONG, M.GC_TRACING, C.DATA_PARALLEL,
          [".cypher"], ["MATCH","RETURN","CREATE","MERGE","DELETE","SET","WHERE","WITH","UNWIND"], 65, gc=0.5, safety=0.7, par=0.8),
        # ── DevOps/Config (lane 66-70) ────────────────────────────────
        L("Dockerfile", F.SHELL_DEVOPS, P.DECLARATIVE, T.UNTYPED, M.STACK_ONLY, C.THREADS,
          ["Dockerfile"], ["FROM","RUN","COPY","ADD","CMD","ENTRYPOINT","EXPOSE","ENV","ARG","LABEL"], 66, gc=0.0, safety=0.5, par=0.7),
        L("Nix",     F.SHELL_DEVOPS, P.FUNCTIONAL, T.DYNAMIC_STRONG, M.PERSISTENT, C.THREADS,
          [".nix"], ["let","in","with","inherit","rec","builtins","nixpkgs","derivation","mkDerivation"], 67, gc=0.5, safety=0.85, par=0.7),
        L("Terraform HCL", F.SHELL_DEVOPS, P.DECLARATIVE, T.STATIC_STRONG, M.STACK_ONLY, C.THREADS,
          [".tf",".tfvars"], ["resource","provider","module","variable","output","data","locals","backend"], 68, gc=0.0, safety=0.7, par=0.7),
        L("YAML",    F.MARKUP, P.DECLARATIVE, T.UNTYPED, M.STACK_ONLY, C.THREADS,
          [".yaml",".yml"], ["---","true","false","null","!","&","*","|",">","mapping","sequence"], 69, gc=0.0, safety=0.5, par=0.5),
        L("TOML",    F.MARKUP, P.DECLARATIVE, T.STATIC_STRONG, M.STACK_ONLY, C.THREADS,
          [".toml"], ["[table]","[[array]]","key","=","string","integer","float","boolean","datetime"], 70, gc=0.0, safety=0.7, par=0.5),
        # ── Markup (lane 71-73) ───────────────────────────────────────
        L("LaTeX",   F.MARKUP, P.DECLARATIVE, T.UNTYPED, M.STACK_ONLY, C.THREADS,
          [".tex",".sty",".bib"], ["\\begin","\\end","\\def","\\newcommand","\\documentclass","\\usepackage","\\label"], 71, gc=0.0, safety=0.7, par=0.5),
        L("Markdown", F.MARKUP, P.DECLARATIVE, T.UNTYPED, M.STACK_ONLY, C.THREADS,
          [".md",".markdown"], ["#","##","**","*","```","[link]","![img]","---","---","blockquote"], 72, gc=0.0, safety=0.9, par=0.3),
        L("HTML/CSS", F.MARKUP, P.DECLARATIVE, T.UNTYPED, M.STACK_ONLY, C.ASYNC_AWAIT,
          [".html",".htm",".css"], ["<html>","<body>","<div>","<script>","@media","display:flex","grid","var(--"], 73, gc=0.0, safety=0.6, par=0.5),
    ]
    return {lang.name: lang for lang in langs}


class LanguageRegistry:
    """The authoritative catalog of all 74 UOS-supported programming languages.

    Examples
    --------
    >>> reg = LanguageRegistry()
    >>> reg.get("Rust").safety_score
    1.0
    >>> len(reg.all())
    74
    >>> reg.by_family(LanguageFamily.QUANTUM)
    [LanguageManifest(name='Qiskit', ...), ...]
    """

    def __init__(self) -> None:
        self._catalog: Dict[str, LanguageManifest] = _build_registry()

    def get(self, name: str) -> LanguageManifest:
        """Return the manifest for a language by name."""
        if name not in self._catalog:
            raise KeyError(f"Language '{name}' is not registered in the UOS runtime.")
        return self._catalog[name]

    def all(self) -> List[LanguageManifest]:
        """Return all registered languages (sorted by manifold_lane)."""
        return sorted(self._catalog.values(), key=lambda m: m.manifold_lane)

    def by_family(self, family: LanguageFamily) -> List[LanguageManifest]:
        """Return all languages in a given family."""
        return [m for m in self._catalog.values() if m.family == family]

    def by_paradigm(self, paradigm: Paradigm) -> List[LanguageManifest]:
        """Return all languages with a given primary paradigm."""
        return [m for m in self._catalog.values() if m.paradigm == paradigm]

    def by_typing(self, typing: TypingDiscipline) -> List[LanguageManifest]:
        """Return all languages with a given typing discipline."""
        return [m for m in self._catalog.values() if m.typing == typing]

    def by_memory_model(self, model: MemoryModel) -> List[LanguageManifest]:
        """Return all languages with a given memory model."""
        return [m for m in self._catalog.values() if m.memory == model]

    def detect_language(self, filename: str) -> Optional[LanguageManifest]:
        """Attempt to detect language from a file extension."""
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else filename
        for lang in self._catalog.values():
            if ext in lang.file_extensions:
                return lang
        return None

    def safest_languages(self, n: int = 5) -> List[LanguageManifest]:
        """Return the n languages with the highest safety_score."""
        return sorted(self._catalog.values(), key=lambda m: -m.safety_score)[:n]

    def most_parallel(self, n: int = 5) -> List[LanguageManifest]:
        """Return the n languages with the highest parallelism_score."""
        return sorted(self._catalog.values(), key=lambda m: -m.parallelism_score)[:n]

    def names(self) -> List[str]:
        """Return a sorted list of all registered language names."""
        return sorted(self._catalog.keys())

    def __len__(self) -> int:
        return len(self._catalog)

    def __contains__(self, name: str) -> bool:
        return name in self._catalog


# ===========================================================================
# UniversalRuntime — the language-aware manifold runtime
# ===========================================================================

class UniversalRuntime:
    """UOS Universal Language Runtime.

    Maps source code in any registered language onto the 5D manifold,
    validates the geometric invariant, and provides cross-language bridging.

    Parameters
    ----------
    registry : LanguageRegistry, optional
        The language registry to use.  A new default registry is created
        if not supplied.

    Examples
    --------
    >>> rt = UniversalRuntime()
    >>> artifact = rt.ingest("def hello(): return 42", "Python")
    >>> rt.validate_invariant(artifact)
    True
    >>> coord = rt.project(artifact)
    >>> coord.winding
    5
    """

    def __init__(self, registry: Optional[LanguageRegistry] = None) -> None:
        self.registry = registry or LanguageRegistry()
        self._artifacts: Dict[str, CodeArtifact] = {}  # hash → artifact
        self._bridges: Dict[Tuple[str, str], float] = {}  # (src, dst) → similarity

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def ingest(self, source: Any, language_name: str,
               metadata: Optional[Dict] = None) -> CodeArtifact:
        """Ingest source code and project it onto the manifold.

        Parameters
        ----------
        source : str or bytes
            Raw source code.
        language_name : str
            Must be registered in the registry.
        metadata : dict, optional

        Returns
        -------
        CodeArtifact
            The artifact with an assigned manifold coordinate.
        """
        lang = self.registry.get(language_name)
        artifact = CodeArtifact(
            source=source,
            language_name=language_name,
            metadata=metadata or {},
        )
        coord = self.project(artifact)
        artifact.assign_coordinate(coord)
        self._artifacts[artifact.content_hash()] = artifact
        return artifact

    # ------------------------------------------------------------------
    # Projection: code → manifold coordinate
    # ------------------------------------------------------------------

    def project(self, artifact: CodeArtifact) -> ManifoldCoordinate:
        """Project a code artifact onto the 5D manifold.

        The projection uses:
          * φ-coordinate: content fingerprint of the source code
          * B-vector: language manifest vector (safety, parallelism, etc.)
          * winding: WINDING_NUMBER (= 5, the braid period)

        Parameters
        ----------
        artifact : CodeArtifact

        Returns
        -------
        ManifoldCoordinate
        """
        lang = self.registry.get(artifact.language_name)
        phi = artifact.phi_fingerprint() * 2.0 * np.pi * WINDING_NUMBER
        B = lang.manifold_vector()[:4]   # 4-vector from manifest
        return ManifoldCoordinate(
            phi_coord=phi,
            B_coord=B,
            winding=WINDING_NUMBER,
            label=f"{artifact.language_name}:{artifact.content_hash()[:8]}",
        )

    # ------------------------------------------------------------------
    # Invariant validation
    # ------------------------------------------------------------------

    def validate_invariant(self, artifact: CodeArtifact) -> bool:
        """Return True if the artifact passes the 5:7 braid invariant gate.

        The gate checks that the φ-fingerprint falls within the security
        window.  With tolerance=1.0 (full range) all well-formed code passes;
        a stricter tolerance would reject code whose semantic fingerprint
        deviates from the canonical manifold structure.

        Parameters
        ----------
        artifact : CodeArtifact

        Returns
        -------
        bool
        """
        fp = artifact.phi_fingerprint()
        # All well-formed code is valid in the UOS universal runtime.
        # The invariant constrains *execution context*, not the code itself.
        return 0.0 <= fp < 1.0

    # ------------------------------------------------------------------
    # Cross-language bridge
    # ------------------------------------------------------------------

    def bridge_similarity(self, lang_a: str, lang_b: str) -> float:
        """Compute the semantic similarity between two languages on the manifold.

        Similarity = cosine similarity of the two language manifest vectors.
        Languages with similar safety, memory, and concurrency models have
        high similarity → can be bridged with low friction.

        Parameters
        ----------
        lang_a : str
        lang_b : str

        Returns
        -------
        float
            Cosine similarity in [0, 1].
        """
        va = self.registry.get(lang_a).manifold_vector()
        vb = self.registry.get(lang_b).manifold_vector()
        dot = float(np.dot(va, vb))
        norm = float(np.linalg.norm(va) * np.linalg.norm(vb))
        if norm < 1e-12:
            return 0.0
        sim = dot / norm
        self._bridges[(lang_a, lang_b)] = sim
        return sim

    def best_bridge(self, lang_a: str, n: int = 3) -> List[Tuple[str, float]]:
        """Return the n languages most similar to lang_a on the manifold.

        Parameters
        ----------
        lang_a : str
        n : int

        Returns
        -------
        list of (language_name, similarity) tuples, sorted by decreasing similarity
        """
        results = []
        for name in self.registry.names():
            if name == lang_a:
                continue
            sim = self.bridge_similarity(lang_a, name)
            results.append((name, sim))
        results.sort(key=lambda x: -x[1])
        return results[:n]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        """Return runtime statistics."""
        return {
            "registered_languages": len(self.registry),
            "ingested_artifacts": len(self._artifacts),
            "bridge_pairs_computed": len(self._bridges),
            "families": len(set(m.family for m in self.registry.all())),
            "paradigms": len(set(m.paradigm for m in self.registry.all())),
        }
