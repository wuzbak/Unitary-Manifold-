# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_uos_language_runtime.py — tests for UOS/language_runtime.py

Covers: LanguageManifest, LanguageRegistry, CodeArtifact,
        ManifoldCoordinate, UniversalRuntime (74 languages).
"""

import sys, os
_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_PENTAD_DIR, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

import numpy as np
import pytest

from UOS.language_runtime import (
    LanguageManifest, LanguageFamily, LanguageRegistry, Paradigm,
    TypingDiscipline, MemoryModel, ConcurrencyModel,
    CodeArtifact, ManifoldCoordinate, UniversalRuntime,
)
from UOS.constants import WINDING_NUMBER, K_CS, PHI_BACKGROUND


# ===========================================================================
# LanguageRegistry
# ===========================================================================

class TestLanguageRegistry:
    def _reg(self):
        return LanguageRegistry()

    def test_exactly_74_languages(self):
        assert len(self._reg()) == K_CS

    def test_all_have_unique_lanes(self):
        reg = self._reg()
        lanes = [m.manifold_lane for m in reg.all()]
        assert len(set(lanes)) == K_CS, "Every lane must be unique"

    def test_lanes_cover_0_to_73(self):
        reg = self._reg()
        lanes = sorted(m.manifold_lane for m in reg.all())
        assert lanes == list(range(K_CS))

    def test_get_rust(self):
        reg = self._reg()
        rust = reg.get("Rust")
        assert rust.name == "Rust"
        assert rust.safety_score == 1.0

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError):
            self._reg().get("COBOL-1959")

    def test_contains_python(self):
        assert "Python" in self._reg()

    def test_contains_rust(self):
        assert "Rust" in self._reg()

    def test_contains_haskell(self):
        assert "Haskell" in self._reg()

    def test_contains_prolog(self):
        assert "Prolog" in self._reg()

    def test_contains_qiskit(self):
        assert "Qiskit" in self._reg()

    def test_contains_sql(self):
        assert "SQL" in self._reg()

    def test_contains_verilog(self):
        assert "Verilog" in self._reg()

    def test_contains_webassembly(self):
        assert "WebAssembly" in self._reg()

    def test_by_family_quantum(self):
        reg = self._reg()
        q = reg.by_family(LanguageFamily.QUANTUM)
        names = [m.name for m in q]
        assert "Qiskit" in names
        assert "Cirq" in names
        assert "Q#" in names
        assert "Quipper" in names

    def test_by_family_systems(self):
        reg = self._reg()
        sys_langs = reg.by_family(LanguageFamily.SYSTEMS)
        names = [m.name for m in sys_langs]
        assert "Rust" in names
        assert "C" in names
        assert "Go" in names

    def test_by_family_jvm(self):
        reg = self._reg()
        jvm = reg.by_family(LanguageFamily.JVM)
        names = [m.name for m in jvm]
        assert "Java" in names
        assert "Kotlin" in names
        assert "Scala" in names

    def test_by_paradigm_functional(self):
        reg = self._reg()
        fns = reg.by_paradigm(Paradigm.FUNCTIONAL)
        assert len(fns) >= 4

    def test_by_typing_static_strong(self):
        reg = self._reg()
        ss = reg.by_typing(TypingDiscipline.STATIC_STRONG)
        names = [m.name for m in ss]
        assert "Rust" in names
        assert "Haskell" in names

    def test_by_memory_model_ownership(self):
        reg = self._reg()
        owned = reg.by_memory_model(MemoryModel.OWNERSHIP)
        assert any(m.name == "Rust" for m in owned)

    def test_detect_language_by_extension_rs(self):
        reg = self._reg()
        lang = reg.detect_language("main.rs")
        assert lang is not None
        assert lang.name == "Rust"

    def test_detect_language_by_extension_py(self):
        reg = self._reg()
        lang = reg.detect_language("script.py")
        assert lang is not None
        assert lang.name == "Python"

    def test_detect_language_by_extension_ts(self):
        reg = self._reg()
        lang = reg.detect_language("app.ts")
        assert lang is not None
        assert lang.name == "TypeScript"

    def test_detect_language_by_extension_go(self):
        reg = self._reg()
        lang = reg.detect_language("server.go")
        assert lang is not None
        assert lang.name == "Go"

    def test_detect_language_unknown_returns_none(self):
        reg = self._reg()
        assert reg.detect_language("unknown.xyz123") is None

    def test_safest_languages_top_5(self):
        reg = self._reg()
        safest = reg.safest_languages(5)
        # Rust (1.0), Idris (1.0), Agda (1.0) should appear
        names = [m.name for m in safest]
        assert "Rust" in names

    def test_most_parallel_top_5(self):
        reg = self._reg()
        par = reg.most_parallel(5)
        names = [m.name for m in par]
        # Quantum, Erlang, Qiskit etc all 0.99
        assert any(m.parallelism_score >= 0.95 for m in par)

    def test_all_languages_have_keywords(self):
        reg = self._reg()
        for lang in reg.all():
            assert len(lang.keywords) >= 5, f"{lang.name} needs at least 5 keywords"

    def test_all_languages_have_extensions(self):
        reg = self._reg()
        for lang in reg.all():
            assert len(lang.file_extensions) >= 1, f"{lang.name} needs at least 1 extension"

    def test_all_safety_scores_in_range(self):
        reg = self._reg()
        for lang in reg.all():
            assert 0.0 <= lang.safety_score <= 1.0

    def test_all_parallelism_scores_in_range(self):
        reg = self._reg()
        for lang in reg.all():
            assert 0.0 <= lang.parallelism_score <= 1.0

    def test_names_is_sorted(self):
        reg = self._reg()
        names = reg.names()
        assert names == sorted(names)

    def test_len(self):
        assert len(LanguageRegistry()) == K_CS


# ===========================================================================
# LanguageManifest
# ===========================================================================

class TestLanguageManifest:
    def _rust(self):
        return LanguageRegistry().get("Rust")

    def test_phi_coordinate_in_range(self):
        rust = self._rust()
        phi = rust.phi_coordinate()
        assert 0.0 <= phi < 1.0

    def test_phi_deterministic(self):
        reg = LanguageRegistry()
        assert reg.get("Python").phi_coordinate() == reg.get("Python").phi_coordinate()

    def test_manifold_vector_shape(self):
        rust = self._rust()
        v = rust.manifold_vector()
        assert v.shape == (5,)

    def test_manifold_vector_components_in_range(self):
        reg = LanguageRegistry()
        for lang in reg.all():
            v = lang.manifold_vector()
            assert np.all(v >= 0.0), f"{lang.name} manifold_vector has negative component"
            assert np.all(v <= 1.0), f"{lang.name} manifold_vector has component > 1"

    def test_rust_gc_pressure_zero(self):
        assert self._rust().gc_pressure == 0.0

    def test_erlang_concurrency_actor(self):
        erlang = LanguageRegistry().get("Erlang")
        assert erlang.concurrency == ConcurrencyModel.ACTOR

    def test_go_concurrency_csp(self):
        go = LanguageRegistry().get("Go")
        assert go.concurrency == ConcurrencyModel.CSP

    def test_haskell_memory_persistent(self):
        h = LanguageRegistry().get("Haskell")
        assert h.memory == MemoryModel.PERSISTENT

    def test_c_memory_manual(self):
        c = LanguageRegistry().get("C")
        assert c.memory == MemoryModel.MANUAL


# ===========================================================================
# CodeArtifact
# ===========================================================================

class TestCodeArtifact:
    def test_size_bytes_str(self):
        a = CodeArtifact(source="hello", language_name="Python")
        assert a.size_bytes == 5

    def test_size_bytes_bytes(self):
        a = CodeArtifact(source=b"\x00\x01\x02", language_name="C")
        assert a.size_bytes == 3

    def test_content_hash_hex(self):
        a = CodeArtifact(source="fn main(){}", language_name="Rust")
        h = a.content_hash()
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_content_hash_deterministic(self):
        src = "def hello(): return 42"
        a1 = CodeArtifact(source=src, language_name="Python")
        a2 = CodeArtifact(source=src, language_name="Python")
        assert a1.content_hash() == a2.content_hash()

    def test_phi_fingerprint_in_range(self):
        a = CodeArtifact(source="SELECT 1", language_name="SQL")
        assert 0.0 <= a.phi_fingerprint() < 1.0

    def test_loc_nonblank(self):
        src = "def f():\n    pass\n\n    # comment\n    return 1"
        a = CodeArtifact(source=src, language_name="Python")
        assert a.loc() >= 3

    def test_loc_empty(self):
        a = CodeArtifact(source="\n\n\n", language_name="Python")
        assert a.loc() == 0

    def test_token_count(self):
        a = CodeArtifact(source="fn add(a: i32, b: i32) -> i32 { a + b }", language_name="Rust")
        assert a.token_count() >= 5

    def test_assign_and_read_coordinate(self):
        a = CodeArtifact(source="x = 1", language_name="Python")
        coord = ManifoldCoordinate(phi_coord=1.5, B_coord=np.zeros(4), winding=5)
        a.assign_coordinate(coord)
        assert a.coordinate is coord

    def test_coordinate_none_by_default(self):
        a = CodeArtifact(source="x", language_name="Python")
        assert a.coordinate is None


# ===========================================================================
# ManifoldCoordinate
# ===========================================================================

class TestManifoldCoordinate:
    def _make(self, phi=1.0, label="test"):
        return ManifoldCoordinate(phi_coord=phi, B_coord=np.zeros(4),
                                  winding=WINDING_NUMBER, label=label)

    def test_distance_same_point(self):
        c = self._make()
        assert c.distance_to(c) == pytest.approx(0.0, abs=1e-9)

    def test_distance_positive(self):
        a = self._make(phi=0.0)
        b = self._make(phi=1.0)
        assert a.distance_to(b) > 0.0

    def test_distance_symmetric(self):
        a = self._make(phi=0.5)
        b = self._make(phi=2.0)
        assert a.distance_to(b) == pytest.approx(b.distance_to(a), rel=1e-9)

    def test_hash_label_differentiated(self):
        a = ManifoldCoordinate(phi_coord=1.0, B_coord=np.zeros(4),
                               winding=5, label="a")
        b = ManifoldCoordinate(phi_coord=1.0, B_coord=np.zeros(4),
                               winding=5, label="b")
        assert hash(a) != hash(b)


# ===========================================================================
# UniversalRuntime
# ===========================================================================

class TestUniversalRuntime:
    def _rt(self):
        return UniversalRuntime()

    def test_registry_74_languages(self):
        rt = self._rt()
        assert len(rt.registry) == K_CS

    def test_ingest_returns_artifact(self):
        rt = self._rt()
        a = rt.ingest("def hello(): pass", "Python")
        assert isinstance(a, CodeArtifact)

    def test_ingest_assigns_coordinate(self):
        rt = self._rt()
        a = rt.ingest("fn main() {}", "Rust")
        assert a.coordinate is not None

    def test_ingest_coordinate_winding(self):
        rt = self._rt()
        a = rt.ingest("fn main() {}", "Rust")
        assert a.coordinate.winding == WINDING_NUMBER

    def test_validate_invariant_all_languages(self):
        rt = self._rt()
        for lang in rt.registry.names():
            a = rt.ingest(f"# code in {lang}", lang)
            assert rt.validate_invariant(a) is True

    def test_project_phi_in_range(self):
        rt = self._rt()
        a = CodeArtifact(source="x = 42", language_name="Python")
        coord = rt.project(a)
        assert coord.phi_coord >= 0.0

    def test_bridge_similarity_same_lang_near_1(self):
        rt = self._rt()
        # Rust vs Zig (both systems, ownership-ish, static strong)
        sim = rt.bridge_similarity("Rust", "Zig")
        assert sim > 0.8

    def test_bridge_similarity_in_range(self):
        rt = self._rt()
        sim = rt.bridge_similarity("Python", "Haskell")
        assert 0.0 <= sim <= 1.0

    def test_bridge_similarity_symmetric(self):
        rt = self._rt()
        assert rt.bridge_similarity("Java", "Kotlin") == pytest.approx(
            rt.bridge_similarity("Kotlin", "Java"), rel=1e-9
        )

    def test_best_bridge_returns_n(self):
        rt = self._rt()
        results = rt.best_bridge("Python", n=5)
        assert len(results) == 5
        # Each entry is (name, similarity)
        for name, sim in results:
            assert isinstance(name, str)
            assert 0.0 <= sim <= 1.0

    def test_best_bridge_sorted_desc(self):
        rt = self._rt()
        results = rt.best_bridge("Rust", n=5)
        sims = [s for _, s in results]
        assert sims == sorted(sims, reverse=True)

    def test_stats(self):
        rt = self._rt()
        rt.ingest("hello", "Python")
        stats = rt.stats()
        assert stats["registered_languages"] == K_CS
        assert stats["ingested_artifacts"] >= 1

    def test_ingest_unknown_language_raises(self):
        rt = self._rt()
        with pytest.raises(KeyError):
            rt.ingest("x", "COBOL-1959")

    def test_ingest_with_metadata(self):
        rt = self._rt()
        a = rt.ingest("x = 1", "Python", metadata={"author": "Alice"})
        assert a.metadata["author"] == "Alice"

    def test_bridge_rust_vs_c(self):
        rt = self._rt()
        # Rust and C are both systems languages
        sim = rt.bridge_similarity("Rust", "C")
        assert sim > 0.7

    def test_bridge_sql_vs_prolog(self):
        rt = self._rt()
        # Both declarative
        sim = rt.bridge_similarity("SQL", "Prolog")
        assert sim > 0.5

    def test_all_73_bridges_from_python(self):
        rt = self._rt()
        results = rt.best_bridge("Python", n=K_CS - 1)
        assert len(results) == K_CS - 1
