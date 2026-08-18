# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Canonical engine registry with static catalog metadata and auto-discovery support."""
from __future__ import annotations

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)
ENGINES_DIR = Path(__file__).parent

ENGINE_CATALOG: List[Dict[str, str]] = [
    {"name": "field_evolution", "version": "repo", "source": "src/core/evolution.py", "category": "physics"},
    {"name": "kk_metric", "version": "repo", "source": "src/core/metric.py", "category": "physics"},
    {"name": "cmb_transfer", "version": "repo", "source": "src/core/", "category": "physics"},
    {"name": "birefringence", "version": "repo", "source": "src/core/", "category": "physics"},
    {"name": "ftum_fixed_point", "version": "repo", "source": "src/multiverse/fixed_point.py", "category": "physics"},
    {"name": "holographic_boundary", "version": "repo", "source": "src/holography/boundary.py", "category": "physics"},
    {"name": "phi_debt_recycling", "version": "repo", "source": "recycling/", "category": "physics"},
    {"name": "quantum_simulation", "version": "repo", "source": "src/quantum/", "category": "quantum"},
    {"name": "axiomzero_cognitive_ai", "version": "1.0.0", "source": "12-AZ-IP/01-axiom-os/", "category": "ai"},
    {"name": "model_router", "version": "1.0.0", "source": "12-AZ-IP/01-axiom-os/core/model_router.py", "category": "ai"},
    {"name": "phi_field_decision", "version": "1.0.0", "source": "12-AZ-IP/01-axiom-os/phi_decision_engine.py", "category": "ai"},
    {"name": "mas_wave", "version": "repo", "source": "src/meta/", "category": "ai"},
    {"name": "eige_adjudicator", "version": "21.0.0", "source": "12-AZ-IP/03-eige/src/adjudicator_api.py", "category": "governance"},
    {"name": "rag_physics", "version": "repo", "source": "bot/", "category": "ai"},
    {"name": "unitary_pentad", "version": "repo", "source": "5-GOVERNANCE/Unitary Pentad/", "category": "governance"},
]


def _get_engine_class():
    try:
        lib_path = str(ENGINES_DIR.parent / "lib")
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        from az_ip_common.engine import Engine, EngineResult
        return Engine, EngineResult
    except ImportError:
        return None, None


class EngineRegistry:
    def __init__(self) -> None:
        self._engines: Dict[str, object] = {}
        self._classes: Dict[str, Type] = {}
        self._loaded = False

    def catalog(self) -> List[Dict[str, str]]:
        return list(ENGINE_CATALOG)

    def load(self) -> int:
        Engine, _ = _get_engine_class()
        if Engine is None:
            logger.warning("az_ip_common not available — engine discovery disabled")
            return 0
        discovered = 0
        for py_file in sorted(ENGINES_DIR.glob('*.py')):
            if py_file.stem in ('engine_registry', '__init__'):
                continue
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                for attr_name in dir(mod):
                    obj = getattr(mod, attr_name)
                    if inspect.isclass(obj) and issubclass(obj, Engine) and obj is not Engine and hasattr(obj, 'name') and obj.name != 'base_engine':
                        instance = obj()
                        self._engines[obj.name] = instance
                        self._classes[obj.name] = obj
                        discovered += 1
            except Exception as exc:
                logger.warning("Failed to load engine module %s: %s", py_file.name, exc)
        self._loaded = True
        return discovered

    def list_engines(self) -> List[Dict]:
        result = []
        for name, engine in self._engines.items():
            result.append({
                'name': name,
                'version': getattr(engine, 'version', 'unknown'),
                'epistemic_label': getattr(engine, 'epistemic_label', 'UNCLASSIFIED'),
                'class': type(engine).__name__,
            })
        return result

    def get(self, name: str) -> Optional[object]:
        return self._engines.get(name)

    async def run(self, engine_name: str, hils_approved: bool = True, **kwargs):
        engine = self._engines.get(engine_name)
        if engine is None:
            _, EngineResult = _get_engine_class()
            if EngineResult:
                return EngineResult(engine_name=engine_name, version='?', ok=False, data=None, error=f"Engine {engine_name!r} not found")
            raise KeyError(f"Engine {engine_name!r} not found")
        return await engine.run(hils_approved=hils_approved, **kwargs)  # type: ignore[union-attr]

    async def health_all(self) -> Dict[str, Dict]:
        results = {}
        for name, engine in self._engines.items():
            try:
                results[name] = await engine.health()  # type: ignore[union-attr]
            except Exception as exc:
                results[name] = {'ok': False, 'error': str(exc)}
        return results


registry = EngineRegistry()
