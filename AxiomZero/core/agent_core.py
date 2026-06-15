# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero core/agent_core.py — Phase 1: Cognitive Core Orchestrator

7-Manager × 5-Sub-Agent network built on LangGraph with SQLite checkpointing.
Gracefully degrades to stub mode if LangGraph is not installed.

Architecture:
    M1 Geometry & Manifold Engine
    M2 Field Equation Solver
    M3 Symbolic Math & Proof Verifier   ← mandatory gateway for physics claims
    M4 Test Orchestration & CI Guard    ← mandatory gateway for code changes
    M5 Literary Corpus & RAG Engine
    M6 Web Research & OSINT
    M7 Executive Synthesis & Human Interface  ← only manager that talks to human

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional LangGraph import with graceful degradation
# ---------------------------------------------------------------------------
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
    _LANGGRAPH_AVAILABLE = True
except ImportError:
    _LANGGRAPH_AVAILABLE = False
    logger.warning(
        "langgraph not installed — AxiomZero runs in sequential stub mode. "
        "Install: pip install langgraph"
    )


# ---------------------------------------------------------------------------
# Epistemics labels (enforced in every agent prompt)
# ---------------------------------------------------------------------------
class EpistemicLabel(str, Enum):
    HARDGATE = "HARDGATE"           # Core physics pillars 1–208
    ADJACENT_TRACK = "ADJACENT-TRACK"  # Pillars 218–232
    GOVERNANCE = "GOVERNANCE"       # Unitary Pentad
    UNVERIFIED = "UNVERIFIED"       # Pending M3 validation


# ---------------------------------------------------------------------------
# Task / AgentState
# ---------------------------------------------------------------------------
@dataclass
class AgentTask:
    """A unit of work routed through the AxiomZero agent network."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    epistemic_label: EpistemicLabel = EpistemicLabel.HARDGATE
    payload: Dict[str, Any] = field(default_factory=dict)
    cycle_count: int = 0
    max_cycles: int = 5
    results: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending | running | blocked | complete | failed | human_review
    created_at: float = field(default_factory=time.time)
    requires_human_approval: bool = False
    error: Optional[str] = None


@dataclass
class AgentState:
    """Shared state flowing through the LangGraph nodes."""
    task: AgentTask
    m1_output: Optional[Dict] = None
    m2_output: Optional[Dict] = None
    m3_output: Optional[Dict] = None   # Symbolic verification gate
    m4_output: Optional[Dict] = None   # Test gate
    m5_output: Optional[Dict] = None
    m6_output: Optional[Dict] = None
    m7_output: Optional[Dict] = None
    approved: bool = False
    route: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Manager base class
# ---------------------------------------------------------------------------
class BaseManager:
    """Base class for all 7 managers.  Each manager has 5 sub-agents."""

    name: str = "BaseManager"
    model_key: str = "strategic"      # used by ModelRouter
    sub_agents: List[str] = []

    def __init__(self, config: Dict, model_router: Any, repo_root: Path):
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root

    async def run(self, state: AgentState) -> Dict[str, Any]:
        """Override in subclass.  Must return a dict with at least 'status'."""
        raise NotImplementedError

    def _log(self, msg: str) -> None:
        logger.info("[%s] %s", self.name, msg)

    def _label_context(self, state: AgentState) -> str:
        """Inject epistemic label into every prompt context."""
        return (
            f"[EPISTEMIC CONTEXT: {state.task.epistemic_label.value}] "
            f"You are operating within the Unitary Manifold physics framework. "
            f"Human in the loop: ThomasCory Walker-Pearson retains final authority."
        )


# ---------------------------------------------------------------------------
# Import manager implementations
# ---------------------------------------------------------------------------
from AxiomZero.core.manager_geometry import GeometryManager       # M1
from AxiomZero.core.manager_field import FieldManager              # M2
from AxiomZero.core.manager_symbolic import SymbolicManager        # M3
from AxiomZero.core.manager_test import TestManager                # M4
from AxiomZero.core.manager_rag import RAGManager                  # M5
from AxiomZero.core.manager_web import WebManager                  # M6
from AxiomZero.core.manager_executive import ExecutiveManager      # M7
from AxiomZero.core.model_router import ModelRouter


# ---------------------------------------------------------------------------
# AxiomZero Orchestrator
# ---------------------------------------------------------------------------
class AxiomZeroOrchestrator:
    """
    Central orchestrator for the 7-manager cognitive network.

    Usage::

        orchestrator = AxiomZeroOrchestrator.from_config()
        result = await orchestrator.run_task(
            description="Check if Pillar 300 metric derivation is geometrically consistent",
            epistemic_label=EpistemicLabel.HARDGATE,
            payload={"pillar": 300, "file": "src/core/pillar300.py"},
        )
    """

    def __init__(
        self,
        config: Dict,
        repo_root: Path,
        state_db: Optional[Path] = None,
    ):
        self.config = config
        self.repo_root = repo_root
        self.state_db = state_db or Path.home() / ".axiomzero" / "state.db"
        self._model_router = ModelRouter(config.get("models", {}))
        self._tasks: Dict[str, AgentTask] = {}
        self._pending_approvals: Dict[str, AgentTask] = {}

        # Instantiate the 7 managers
        kw = dict(config=config, model_router=self._model_router, repo_root=repo_root)
        self.managers = {
            "m1": GeometryManager(**kw),
            "m2": FieldManager(**kw),
            "m3": SymbolicManager(**kw),
            "m4": TestManager(**kw),
            "m5": RAGManager(**kw),
            "m6": WebManager(**kw),
            "m7": ExecutiveManager(**kw),
        }

        # Build LangGraph or stub
        if _LANGGRAPH_AVAILABLE:
            self._graph = self._build_graph()
        else:
            self._graph = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def from_config(cls, config_path: Optional[Path] = None) -> "AxiomZeroOrchestrator":
        """Load configuration and return a ready orchestrator."""
        if config_path is None:
            config_path = Path.home() / ".axiomzero" / "config.json"

        if config_path.exists():
            config = json.loads(config_path.read_text())
        else:
            # Load defaults
            default = Path(__file__).parent.parent / "config" / "default_config.json"
            config = json.loads(default.read_text()) if default.exists() else {}

        # Resolve repo root
        repo_root_str = config.get("repo_root")
        if repo_root_str:
            repo_root = Path(repo_root_str)
        else:
            repo_root = Path(__file__).parent.parent.parent  # AxiomZero/../ = repo root

        return cls(config=config, repo_root=repo_root)

    async def run_task(
        self,
        description: str,
        epistemic_label: EpistemicLabel = EpistemicLabel.HARDGATE,
        payload: Optional[Dict] = None,
        max_cycles: int = 5,
    ) -> AgentTask:
        """
        Route a task through the agent network.

        Routing logic:
        - All tasks pass through M7 (intake) → M5 (context) → domain managers → M3 (verify) → M4 (test if code) → M7 (output)
        - Code changes additionally require M4 gate + HILS human approval
        - Physics claims additionally require M3 symbolic verification
        """
        task = AgentTask(
            description=description,
            epistemic_label=epistemic_label,
            payload=payload or {},
            max_cycles=max_cycles,
        )
        self._tasks[task.task_id] = task
        task.status = "running"

        logger.info("Task %s started: %s", task.task_id, description)

        try:
            if self._graph is not None:
                state = AgentState(task=task)
                result_state = await self._run_graph(state)
                task = result_state.task
            else:
                # Sequential fallback
                task = await self._run_sequential(task)
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)
            logger.exception("Task %s failed: %s", task.task_id, exc)

        self._tasks[task.task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[AgentTask]:
        return list(self._tasks.values())

    def pending_approvals(self) -> List[AgentTask]:
        """Return tasks awaiting HILS human approval."""
        return [t for t in self._tasks.values() if t.status == "human_review"]

    async def approve_task(self, task_id: str, approved: bool) -> AgentTask:
        """
        HILS gate: human approves or rejects a pending task.
        Only M7 calls this after human interaction.
        """
        task = self._tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task {task_id} not found")
        if task.status != "human_review":
            raise ValueError(f"Task {task_id} is not awaiting approval (status={task.status})")

        if approved:
            task.status = "complete"
            task.results["human_approved"] = True
            logger.info("Task %s approved by human", task_id)
        else:
            task.status = "rejected"
            task.results["human_approved"] = False
            logger.info("Task %s rejected by human", task_id)

        return task

    # ------------------------------------------------------------------
    # LangGraph graph
    # ------------------------------------------------------------------

    def _build_graph(self):
        """Build the LangGraph StateGraph for agent routing."""
        graph = StateGraph(dict)  # State is a plain dict for LangGraph compat

        # Add nodes (one per manager)
        for key, manager in self.managers.items():
            graph.add_node(key, self._make_node(manager))

        # Add cycle-count guard node
        graph.add_node("cycle_guard", self._cycle_guard_node)

        # Entry point: M7 receives all tasks
        graph.set_entry_point("cycle_guard")

        # Routing edges
        graph.add_conditional_edges(
            "cycle_guard",
            self._route_from_guard,
            {
                "m7": "m7",
                "end": END,
                "human_review": END,
            }
        )
        graph.add_edge("m7", "m5")      # M7 → M5 (context retrieval)
        graph.add_edge("m5", "m1")      # M5 → M1 (geometry check)
        graph.add_edge("m1", "m2")      # M1 → M2 (field equations)
        graph.add_edge("m2", "m3")      # M2 → M3 (symbolic verify — mandatory)
        graph.add_conditional_edges(
            "m3",
            self._route_from_m3,
            {"m4": "m4", "end": END, "human_review": END},
        )
        graph.add_conditional_edges(
            "m4",
            self._route_from_m4,
            {"m6": "m6", "end": END, "human_review": END},
        )
        graph.add_edge("m6", "m7")
        graph.add_edge("m7", "cycle_guard")

        return graph.compile()

    def _make_node(self, manager: BaseManager):
        """Wrap a manager's async run() as a LangGraph node callable."""
        async def node_fn(state: dict) -> dict:
            agent_state = state.get("_agent_state")
            if agent_state is None:
                return state
            output = await manager.run(agent_state)
            state[f"{manager.name.lower()}_output"] = output
            return state
        return node_fn

    async def _cycle_guard_node(self, state: dict) -> dict:
        """Increment cycle counter and decide whether to continue."""
        agent_state: AgentState = state.get("_agent_state")
        if agent_state:
            agent_state.task.cycle_count += 1
        return state

    def _route_from_guard(self, state: dict) -> str:
        agent_state: AgentState = state.get("_agent_state")
        if agent_state is None:
            return "end"
        task = agent_state.task
        if task.cycle_count > task.max_cycles:
            task.status = "human_review"
            task.results["escalation_reason"] = f"Exceeded max_cycles={task.max_cycles}"
            logger.warning("Task %s escalated to human after %d cycles", task.task_id, task.cycle_count)
            return "human_review"
        if task.status in ("complete", "failed", "rejected"):
            return "end"
        return "m7"

    def _route_from_m3(self, state: dict) -> str:
        """M3 routes: verified → M4 (if code task), unverified → human_review."""
        agent_state: AgentState = state.get("_agent_state")
        if not agent_state:
            return "end"
        m3 = agent_state.m3_output or {}
        if m3.get("verified") is False:
            agent_state.task.status = "human_review"
            agent_state.task.results["m3_block_reason"] = m3.get("reason", "Symbolic verification failed")
            return "human_review"
        return "m4"

    def _route_from_m4(self, state: dict) -> str:
        """M4 routes: tests pass → M6 (enrich with web), fail → human_review."""
        agent_state: AgentState = state.get("_agent_state")
        if not agent_state:
            return "end"
        m4 = agent_state.m4_output or {}
        if m4.get("tests_passed") is False:
            agent_state.task.status = "human_review"
            agent_state.task.results["m4_block_reason"] = m4.get("reason", "Tests failed")
            return "human_review"
        return "m6"

    async def _run_graph(self, state: AgentState) -> AgentState:
        """Execute the LangGraph graph with the given state."""
        graph_state = {"_agent_state": state}
        final = await self._graph.ainvoke(graph_state)
        return final.get("_agent_state", state)

    # ------------------------------------------------------------------
    # Sequential fallback (when LangGraph is not available)
    # ------------------------------------------------------------------

    async def _run_sequential(self, task: AgentTask) -> AgentTask:
        """Execute managers sequentially as a fallback."""
        state = AgentState(task=task)
        pipeline = [
            ("m5", self.managers["m5"]),   # Context first
            ("m1", self.managers["m1"]),   # Geometry
            ("m2", self.managers["m2"]),   # Field equations
            ("m3", self.managers["m3"]),   # Symbolic gate
            ("m4", self.managers["m4"]),   # Test gate
            ("m6", self.managers["m6"]),   # Web enrichment
            ("m7", self.managers["m7"]),   # Executive synthesis
        ]

        for key, manager in pipeline:
            if task.cycle_count > task.max_cycles:
                task.status = "human_review"
                task.results["escalation_reason"] = "max_cycles exceeded"
                break

            logger.info("Task %s → %s", task.task_id, manager.name)
            try:
                output = await manager.run(state)
                setattr(state, f"{key}_output", output)
                state.route.append(key)

                # Check for hard blocks from M3 and M4
                if key == "m3" and output.get("verified") is False:
                    task.status = "human_review"
                    task.results["m3_block"] = output.get("reason")
                    break
                if key == "m4" and output.get("tests_passed") is False:
                    task.status = "human_review"
                    task.results["m4_block"] = output.get("reason")
                    break

            except Exception as exc:
                logger.error("Manager %s failed: %s", manager.name, exc)
                task.results[f"{key}_error"] = str(exc)

        if task.status == "running":
            task.status = "complete"

        task.results["route"] = state.route
        return task

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict:
        return {
            "langgraph_available": _LANGGRAPH_AVAILABLE,
            "managers": list(self.managers.keys()),
            "active_tasks": len([t for t in self._tasks.values() if t.status == "running"]),
            "pending_approvals": len(self.pending_approvals()),
            "total_tasks": len(self._tasks),
            "model_router_status": self._model_router.status(),
        }
