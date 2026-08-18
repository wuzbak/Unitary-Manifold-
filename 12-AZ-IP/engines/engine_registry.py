# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
12-AZ-IP/engines/engine_registry.py — Auto-discovery engine registry.

Any module in 12-AZ-IP/engines/ that exports a class subclassing Engine
(from az_ip_common) is auto-discovered and registered at startup.

Usage::
    from engine_registry import registry
    await registry.load()
    result = await registry.run("kk_geometry", phi=0.618)
    print(result.data)

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)

ENGINES_DIR = Path(__file__).parent

# Lazily import Engine base class
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
    """
    Auto-discovery registry for AZ-IP engines.

    Scans all .py files in 12-AZ-IP/engines/ (excluding this file and
    __init__.py) for classes that inherit from Engine, then registers them
    by their `name` attribute.
    """

    def __init__(self) -> None:
        self._engines: Dict[str, object] = {}   # name → Engine instance
        self._classes: Dict[str, Type] = {}      # name → Engine subclass
        self._loaded = False

    def load(self) -> int:
        """
        Discover and instantiate all Engine subclasses in the engines directory.
        Returns the number of engines registered.
        """
        Engine, _ = _get_engine_class()
        if Engine is None:
            logger.warning("az_ip_common not available — engine discovery disabled")
            return 0

        discovered = 0
        for py_file in sorted(ENGINES_DIR.glob("*.py")):
            if py_file.stem in ("engine_registry", "__init__"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
                for attr_name in dir(mod):
                    obj = getattr(mod, attr_name)
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, Engine)
                        and obj is not Engine
                        and hasattr(obj, "name")
                        and obj.name != "base_engine"
                    ):
                        instance = obj()
                        self._engines[obj.name] = instance
                        self._classes[obj.name] = obj
                        logger.info("Registered engine: %s v%s", obj.name, obj.version)
                        discovered += 1
            except Exception as exc:
                logger.warning("Failed to load engine module %s: %s", py_file.name, exc)

        self._loaded = True
        logger.info("Engine registry: %d engines loaded", discovered)
        return discovered

    def list_engines(self) -> List[Dict]:
        """Return metadata for all registered engines."""
        result = []
        for name, engine in self._engines.items():
            result.append({
                "name": name,
                "version": getattr(engine, "version", "unknown"),
                "epistemic_label": getattr(engine, "epistemic_label", "UNCLASSIFIED"),
                "class": type(engine).__name__,
            })
        return result

    def get(self, name: str) -> Optional[object]:
        """Return the engine instance for the given name."""
        return self._engines.get(name)

    async def run(self, engine_name: str, hils_approved: bool = True, **kwargs):
        """Run a registered engine by name."""
        engine = self._engines.get(engine_name)
        if engine is None:
            _, EngineResult = _get_engine_class()
            if EngineResult:
                return EngineResult(
                    engine_name=engine_name, version="?", ok=False,
                    data=None, error=f"Engine {engine_name!r} not found",
                )
            raise KeyError(f"Engine {engine_name!r} not found")
        return await engine.run(hils_approved=hils_approved, **kwargs)  # type: ignore[union-attr]

    async def health_all(self) -> Dict[str, Dict]:
        """Run health() on all registered engines."""
        results = {}
        for name, engine in self._engines.items():
            try:
                results[name] = await engine.health()  # type: ignore[union-attr]
            except Exception as exc:
                results[name] = {"ok": False, "error": str(exc)}
        return results


# Module-level singleton
registry = EngineRegistry()
