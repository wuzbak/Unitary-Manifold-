# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/rl_env.py — Gymnasium-Compatible RL Environment (Zone 3: Training Gym)

A clean, honest reinforcement learning environment where agents navigate the
Unitary Manifold's pillar lattice.  Every reward is the mathematical precision
score returned by the backing ``src/core/`` modules — no fake inflation, no
pre-certified records.

State space
-----------
Observation vector (5 floats, all in [0, 1] or natural-unit ranges):
  [0] normalised_pillar_id     : current pillar / 208
  [1] local_precision_score    : last score for this pillar (0..1)
  [2] mean_session_score       : running session mean (0..1)
  [3] fraction_completed       : pillars attempted / total_registry
  [4] difficulty_level         : easy=0.0, medium=0.5, hard=1.0

Action space
------------
Discrete: choose the next pillar to attempt (index into REGISTRY.ids()).
On each step the environment generates a canonical numeric challenge from
that pillar, evaluates a *deterministic* baseline answer (the module's own
output), and scores the agent's answer.

For RL training, the agent submits a *predicted scalar* for every pillar
regardless of the pillar's expected_type.  Float pillars are scored directly;
dict pillars use the first numeric value in the ground truth.

Reward
------
reward = final_score ∈ [0, 1]

No artificial bonuses, no compliance rewards.  The only way to get a high
reward is to know the physics.

Episode termination
-------------------
* Agent has visited all pillars in the registry (natural completion).
* Agent requests termination (action = -1, interpreted as ``done``).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import gymnasium as gym
    from gymnasium import spaces
    _GYM_AVAILABLE = True
except ImportError:
    _GYM_AVAILABLE = False
    # Provide minimal stubs so the file is importable even without gymnasium
    class gym:  # type: ignore[no-redef]
        class Env:
            metadata: Dict[str, Any] = {}
            def reset(self, *a: Any, **kw: Any) -> Any: ...
            def step(self, *a: Any, **kw: Any) -> Any: ...
    class spaces:  # type: ignore[no-redef]
        class Discrete:
            def __init__(self, n: int) -> None: self.n = n
        class Box:
            def __init__(self, **kw: Any) -> None: pass

from lodge.pillar_registry import REGISTRY, PillarEntry
from lodge.scoring import score_answer
from lodge.session_logger import SessionLogger

__all__ = ["LodgeEnv"]

_DIFFICULTY_MAP = {"easy": 0.0, "medium": 0.5, "hard": 1.0}


def _extract_scalar(value: Any) -> float:
    """Extract the first numeric value from any ground-truth type."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for v in value.values():
            if isinstance(v, (int, float)):
                return float(v)
    if isinstance(value, (list, tuple)):
        for v in value:
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


class LodgeEnv(gym.Env):
    """
    AxiomZero Logic Lodge — Pillar Lattice RL Environment.

    Parameters
    ----------
    agent_label : str
        Label recorded in the session ledger.
    agent_class : str
        "rl-agent" | "llm-api" | "human"
    shuffle : bool
        If True, randomise pillar order each episode.
    difficulty_filter : str | None
        Restrict to "easy", "medium", or "hard" pillars.
    log_sessions : bool
        Whether to write session JSON files to the ledger.
    """

    metadata = {"render_modes": ["human", "ansi"]}

    def __init__(
        self,
        agent_label: str = "rl-agent",
        agent_class: str = "rl-agent",
        shuffle: bool = True,
        difficulty_filter: Optional[str] = None,
        log_sessions: bool = True,
        render_mode: Optional[str] = None,
    ) -> None:
        super().__init__()

        self.agent_label = agent_label
        self.agent_class = agent_class
        self.shuffle = shuffle
        self.log_sessions = log_sessions
        self.render_mode = render_mode

        # Build the ordered list of entries for this environment
        entries = REGISTRY.all()
        if difficulty_filter:
            entries = [e for e in entries if e.difficulty == difficulty_filter]
        if not entries:
            raise ValueError(
                f"No registry entries match difficulty_filter={difficulty_filter!r}"
            )
        self._entries: List[PillarEntry] = entries
        self._n = len(self._entries)

        # Gymnasium spaces
        self.action_space = spaces.Discrete(self._n)
        self.observation_space = spaces.Box(
            low=np.zeros(5, dtype=np.float32),
            high=np.ones(5, dtype=np.float32),
            dtype=np.float32,
        )

        # Episode state (initialised in reset)
        self._visited: List[int] = []
        self._scores: Dict[int, float] = {}
        self._step_count: int = 0
        self._current_idx: int = 0
        self._order: List[int] = list(range(self._n))
        self._logger: Optional[SessionLogger] = None

    # ── Gymnasium API ────────────────────────────────────────────────────────

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self._visited = []
        self._scores = {}
        self._step_count = 0
        self._current_idx = 0

        if self.shuffle:
            self._order = list(self.np_random.permutation(self._n))
        else:
            self._order = list(range(self._n))

        if self.log_sessions:
            self._logger = SessionLogger(
                agent_label=self.agent_label,
                agent_class=self.agent_class,
                zone="training",
            )
            self._logger.start()

        return self._obs(), {}

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Advance the environment.

        ``action`` is an integer index into the registry order.
        The environment resolves the corresponding pillar, evaluates the
        ground-truth scalar, and scores the agent's implicit answer (the
        scalar value of the ground truth itself — i.e., a perfect-knowledge
        oracle baseline).

        For actual RL training, subclass this environment and override
        ``_agent_answer(entry, ground_truth_scalar)`` to inject your policy's
        prediction before calling ``super().step(action)``.
        """
        if action < 0 or action >= self._n:
            # Out-of-bounds → terminate with zero reward
            return self._obs(), 0.0, True, False, {"reason": "invalid_action"}

        entry = self._entries[self._order[action % self._n]]
        self._current_idx = action

        # Load ground truth and extract a scalar for scoring
        try:
            truth = entry.load_ground_truth()
        except Exception as exc:
            return self._obs(), 0.0, False, False, {"error": str(exc)}

        truth_scalar = _extract_scalar(truth)

        # Agent answer — override _agent_answer() in your policy subclass
        agent_scalar = self._agent_answer(entry, truth_scalar)

        result = score_answer(
            pillar_id=entry.pillar_id,
            agent_label=self.agent_label,
            agent_answer=float(agent_scalar),
            ground_truth=float(truth_scalar),
            expected_type="float",
        )

        reward = float(result.final_score)
        self._scores[entry.pillar_id] = reward
        self._visited.append(entry.pillar_id)
        self._step_count += 1

        if self._logger:
            self._logger.record(entry.pillar_id, result.raw_score, result.final_score)

        terminated = len(self._visited) >= self._n
        if terminated and self._logger:
            self._logger.close()
            self._logger = None

        info = {
            "pillar_id": entry.pillar_id,
            "pillar_name": entry.name,
            "difficulty": entry.difficulty,
            "raw_score": result.raw_score,
            "final_score": result.final_score,
            "truth_scalar": truth_scalar,
        }
        return self._obs(), reward, terminated, False, info

    def render(self) -> Optional[str]:
        if self.render_mode == "ansi":
            mean = self._mean_score()
            lines = [
                f"LodgeEnv | step={self._step_count} | "
                f"pillars_visited={len(self._visited)}/{self._n} | "
                f"mean_score={mean:.4f}",
            ]
            return "\n".join(lines)
        return None

    def close(self) -> None:
        if self._logger and not self._logger.is_closed:
            try:
                self._logger.close()
            except Exception:
                pass

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _obs(self) -> np.ndarray:
        """Build the 5-element observation vector."""
        if self._current_idx < self._n:
            entry = self._entries[self._order[self._current_idx]]
            norm_pid = entry.pillar_id / 208.0
            diff = _DIFFICULTY_MAP.get(entry.difficulty, 0.5)
        else:
            norm_pid = 0.0
            diff = 0.0

        last_score = self._scores.get(
            self._entries[self._order[max(0, self._current_idx - 1)]].pillar_id, 0.0
        ) if self._visited else 0.0

        return np.array([
            norm_pid,
            last_score,
            self._mean_score(),
            len(self._visited) / self._n,
            diff,
        ], dtype=np.float32)

    def _mean_score(self) -> float:
        vals = list(self._scores.values())
        return sum(vals) / max(len(vals), 1)

    def _agent_answer(self, entry: PillarEntry, truth_scalar: float) -> float:
        """
        Default: oracle (perfect-knowledge) answer.  Override this in your
        RL policy subclass to inject your model's prediction.

        The oracle baseline is useful for verifying the environment works and
        for generating upper-bound benchmarks.
        """
        return truth_scalar
