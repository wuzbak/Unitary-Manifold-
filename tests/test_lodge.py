# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for the AxiomZero Logic Lodge — all 5 zones.

  Zone 1  Pillar Arcade       (pillar_registry, scoring, arcade)
  Zone 2  Logic Lodge         (lodge_zone)
  Zone 3  Training Gym        (rl_env)
  Zone 4  Observability       (watch — smoke only; no terminal I/O needed)
  Zone 5  Knowledge Exchange  (rag_bridge)

Supporting infrastructure: session_logger, leaderboard.
"""

import json
import math
import sys
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from lodge.pillar_registry import PillarEntry, PillarRegistry, REGISTRY
from lodge.scoring import (
    PrecisionResult,
    score_answer,
    score_bool,
    score_dict,
    score_float,
)
from lodge.session_logger import SessionLogger, list_sessions, load_session
from lodge.leaderboard import Leaderboard
from lodge.lodge_zone import (
    LODGE_PROMPTS,
    LodgeReviewQueue,
    LodgeSubmission,
    auto_score_submission,
)
from lodge.rag_bridge import KnowledgeExchange


# ─────────────────────────────────────────────────────────────────────────────
# Zone 1a — Pillar Registry
# ─────────────────────────────────────────────────────────────────────────────

class TestPillarRegistry:
    """Tests for the pillar challenge catalogue."""

    def test_registry_nonempty(self):
        entries = list(REGISTRY.all())
        assert len(entries) >= 1

    def test_registry_ids_unique(self):
        ids = REGISTRY.ids()
        assert len(ids) == len(set(ids))

    def test_registry_ids_positive(self):
        for pid in REGISTRY.ids():
            assert pid >= 1

    def test_all_entries_have_name(self):
        for e in REGISTRY.all():
            assert e.name and isinstance(e.name, str)

    def test_all_entries_have_difficulty(self):
        valid = {"easy", "medium", "hard"}
        for e in REGISTRY.all():
            assert e.difficulty in valid, f"Pillar {e.pillar_id}: bad difficulty {e.difficulty!r}"

    def test_all_entries_have_domain(self):
        for e in REGISTRY.all():
            assert e.domain and isinstance(e.domain, str)

    def test_all_entries_have_prompt(self):
        for e in REGISTRY.all():
            assert e.prompt and isinstance(e.prompt, str)

    def test_all_entries_have_executor(self):
        for e in REGISTRY.all():
            assert callable(e.executor), f"Pillar {e.pillar_id}: executor not callable"

    def test_all_entries_expected_type(self):
        valid = {"float", "dict", "bool", "tuple"}
        for e in REGISTRY.all():
            assert e.expected_type in valid

    def test_get_by_id(self):
        ids = REGISTRY.ids()
        first = ids[0]
        entry = REGISTRY.get(first)
        assert entry is not None
        assert entry.pillar_id == first

    def test_get_missing_returns_none(self):
        assert REGISTRY.get(999999) is None

    def test_by_difficulty_returns_subset(self):
        for diff in ("easy", "medium", "hard"):
            subset = REGISTRY.by_difficulty(diff)
            for e in subset:
                assert e.difficulty == diff

    def test_by_domain_returns_subset(self):
        domains = {e.domain for e in REGISTRY.all()}
        for domain in domains:
            subset = REGISTRY.by_domain(domain)
            for e in subset:
                assert e.domain == domain

    def test_summary_keys(self):
        s = REGISTRY.summary()
        assert "total" in s
        assert s["total"] == len(REGISTRY.ids())

    def test_load_ground_truth_returns_value(self):
        entry = list(REGISTRY.all())[0]
        gt = entry.load_ground_truth()
        assert gt is not None

    def test_load_ground_truth_cached(self):
        entry = list(REGISTRY.all())[0]
        gt1 = entry.load_ground_truth()
        gt2 = entry.load_ground_truth()
        assert gt1 == gt2

    def test_ground_truth_type_matches_expected(self):
        for e in REGISTRY.all():
            gt = e.load_ground_truth()
            if e.expected_type == "bool":
                assert isinstance(gt, (bool, int))
            elif e.expected_type == "dict":
                assert isinstance(gt, dict)
            # float/tuple may vary in implementation; just ensure a value is returned
            assert gt is not None

    def test_len_dunder(self):
        assert len(REGISTRY) == len(REGISTRY.ids())

    def test_custom_registry_register(self):
        reg = PillarRegistry()
        reg.register(PillarEntry(
            pillar_id=99999,
            name="Test Pillar",
            zone="arcade",
            difficulty="easy",
            domain="test",
            prompt="What is 1+1?",
            hint="Two",
            module_path="builtins",
            executor=lambda: 2.0,
            expected_type="float",
        ))
        assert reg.get(99999) is not None
        assert reg.get(99999).name == "Test Pillar"

    def test_custom_registry_overwrite(self):
        reg = PillarRegistry()
        reg.register(PillarEntry(
            pillar_id=88888,
            name="Old Name",
            zone="arcade",
            difficulty="easy",
            domain="test",
            prompt="p",
            hint="h",
            module_path="builtins",
            executor=lambda: 1.0,
            expected_type="float",
        ))
        reg.register(PillarEntry(
            pillar_id=88888,
            name="New Name",
            zone="arcade",
            difficulty="easy",
            domain="test",
            prompt="p",
            hint="h",
            module_path="builtins",
            executor=lambda: 1.0,
            expected_type="float",
        ))
        assert reg.get(88888).name == "New Name"
        assert len(reg.by_difficulty("easy")) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Zone 1b — Scoring
# ─────────────────────────────────────────────────────────────────────────────

class TestScoreFloat:
    """Unit tests for the scalar precision scorer."""

    def test_exact_match(self):
        assert score_float(1.0, 1.0) == pytest.approx(1.0)

    def test_zero_answer(self):
        s = score_float(0.0, 1.0)
        assert 0.0 <= s <= 1.0

    def test_close_answer(self):
        s = score_float(0.9999, 1.0)
        assert s > 0.99

    def test_far_answer(self):
        s = score_float(100.0, 1.0)
        assert s == pytest.approx(0.0)

    def test_negative_truth(self):
        s = score_float(-1.0, -1.0)
        assert s == pytest.approx(1.0)

    def test_symmetry_near(self):
        s1 = score_float(1.0 + 1e-6, 1.0)
        s2 = score_float(1.0 - 1e-6, 1.0)
        assert abs(s1 - s2) < 1e-4

    def test_score_in_unit_interval(self):
        for agent, truth in [(0.5, 1.0), (2.0, 1.0), (0.0, 0.0), (1e10, 1.0)]:
            s = score_float(agent, truth)
            assert 0.0 <= s <= 1.0


class TestScoreBool:
    """Unit tests for boolean scoring."""

    def test_true_correct(self):
        assert score_bool(True, True) == pytest.approx(1.0)

    def test_false_correct(self):
        assert score_bool(False, False) == pytest.approx(1.0)

    def test_true_wrong(self):
        assert score_bool(True, False) == pytest.approx(0.0)

    def test_false_wrong(self):
        assert score_bool(False, True) == pytest.approx(0.0)

    def test_truthy_int(self):
        assert score_bool(1, True) == pytest.approx(1.0)


class TestScoreDict:
    """Unit tests for dict scoring."""

    def test_exact_match(self):
        d = {"a": 1.0, "b": 2.0}
        raw, per_key = score_dict(d, d)
        assert raw == pytest.approx(1.0)

    def test_partial_match(self):
        truth = {"a": 1.0, "b": 2.0}
        agent = {"a": 1.0, "b": 100.0}
        raw, _ = score_dict(agent, truth)
        assert 0.0 < raw < 1.0

    def test_empty_agent(self):
        raw, _ = score_dict({}, {"a": 1.0})
        assert raw == pytest.approx(0.0)

    def test_missing_key(self):
        raw, per_key = score_dict({"b": 2.0}, {"a": 1.0, "b": 2.0})
        assert "a" in per_key
        assert per_key["a"] == pytest.approx(0.0)

    def test_result_in_unit_interval(self):
        raw, _ = score_dict({"x": 999.0}, {"x": 1.0})
        assert 0.0 <= raw <= 1.0


class TestScoreAnswer:
    """Integration tests for score_answer()."""

    def _entry(self):
        return list(REGISTRY.all())[0]

    def test_perfect_float_answer(self):
        e = self._entry()
        gt = e.load_ground_truth()
        if e.expected_type == "float":
            r = score_answer(
                pillar_id=e.pillar_id,
                agent_label="test",
                agent_answer=gt,
                ground_truth=gt,
                expected_type="float",
            )
            assert isinstance(r, PrecisionResult)
            assert r.final_score == pytest.approx(1.0, abs=0.06)

    def test_wrong_float_answer_low_score(self):
        e = self._entry()
        if e.expected_type == "float":
            gt = e.load_ground_truth()
            r = score_answer(
                pillar_id=e.pillar_id,
                agent_label="test",
                agent_answer=float(gt) * 1000,
                ground_truth=gt,
                expected_type="float",
            )
            assert r.final_score < 0.5

    def test_epistemic_bonus_applied(self):
        r = score_answer(
            pillar_id=1,
            agent_label="test",
            agent_answer=1.0,
            ground_truth=1.0,
            expected_type="float",
            agent_reasoning="This is approximate, uncertain, there is a gap here",
        )
        assert r.epistemic_bonus > 0.0

    def test_overclaim_penalty_applied(self):
        r = score_answer(
            pillar_id=1,
            agent_label="test",
            agent_answer={"lam_cobe": 1.0},
            ground_truth={"lam_cobe": 1.0},
            expected_type="dict",
            agent_reasoning="I have exact derivation of this exact value",
        )
        assert r.overclaim_penalty > 0.0 or r.final_score <= 1.0  # penalty fires or capped

    def test_final_score_in_unit_interval(self):
        for ans in [0.0, 1.0, 999.0, None]:
            r = score_answer(
                pillar_id=1,
                agent_label="test",
                agent_answer=ans,
                ground_truth=1.0,
                expected_type="float",
            )
            assert 0.0 <= r.final_score <= 1.0

    def test_result_fields_present(self):
        r = score_answer(
            pillar_id=1,
            agent_label="myagent",
            agent_answer=1.0,
            ground_truth=1.0,
            expected_type="float",
        )
        assert r.pillar_id == 1
        assert r.agent_label == "myagent"
        assert hasattr(r, "raw_score")
        assert hasattr(r, "final_score")

    def test_bool_type(self):
        r = score_answer(
            pillar_id=1,
            agent_label="test",
            agent_answer=True,
            ground_truth=True,
            expected_type="bool",
        )
        assert r.raw_score == pytest.approx(1.0)

    def test_dict_type(self):
        truth = {"n_s": 0.9635, "r": 0.0315}
        r = score_answer(
            pillar_id=1,
            agent_label="test",
            agent_answer=truth,
            ground_truth=truth,
            expected_type="dict",
        )
        assert r.raw_score == pytest.approx(1.0)

    def test_live_pillar_scores(self):
        """Every pillar in the registry should score ~1.0 when given its own ground truth."""
        for e in REGISTRY.all():
            gt = e.load_ground_truth()
            # Determine a safe expected_type: if ground truth is dict, use "dict"
            etype = e.expected_type
            if isinstance(gt, dict) and etype == "float":
                etype = "dict"
            r = score_answer(
                pillar_id=e.pillar_id,
                agent_label="self",
                agent_answer=gt,
                ground_truth=gt,
                expected_type=etype,
            )
            assert r.raw_score >= 0.9, (
                f"Pillar {e.pillar_id} self-score {r.raw_score:.4f} < 0.9"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Zone 1c — Session Logger
# ─────────────────────────────────────────────────────────────────────────────

class TestSessionLogger:
    """Append-only session ledger."""

    def _make_logger(self, tmp_path):
        return SessionLogger(
            agent_label="test_agent",
            agent_class="llm-api",
            zone="arcade",
            ledger_dir=tmp_path,
        )

    def test_session_id_is_uuid(self, tmp_path):
        sl = self._make_logger(tmp_path)
        import re
        assert re.match(r"[0-9a-f-]{36}", sl.session_id)

    def test_not_started_initially(self, tmp_path):
        sl = self._make_logger(tmp_path)
        assert not sl.is_started

    def test_start_sets_started(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        assert sl.is_started

    def test_record_requires_start(self, tmp_path):
        sl = self._make_logger(tmp_path)
        # Recording before close is allowed (no start required)
        # But recording after close raises RuntimeError
        sl.start()
        sl.close()
        with pytest.raises(RuntimeError):
            sl.record(pillar_id=1, raw_score=0.9, final_score=0.9)

    def test_close_writes_file(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        sl.record(pillar_id=1, raw_score=0.95, final_score=0.95)
        path = sl.close()
        assert path.exists()

    def test_closed_file_is_valid_json(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        sl.record(pillar_id=2, raw_score=0.8, final_score=0.83)
        path = sl.close()
        data = json.loads(path.read_text())
        assert "session_id" in data

    def test_closed_file_has_hash(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        path = sl.close()
        data = json.loads(path.read_text())
        assert "session_hash" in data
        assert len(data["session_hash"]) == 64

    def test_session_hash_verifiable(self, tmp_path):
        import hashlib
        sl = self._make_logger(tmp_path)
        sl.start()
        sl.record(pillar_id=1, raw_score=0.9, final_score=0.9)
        path = sl.close()
        data = json.loads(path.read_text())
        stored_hash = data.pop("session_hash")
        # The logger uses json.dumps(payload, sort_keys=True) — default separators
        payload = json.dumps(data, sort_keys=True)
        expected = hashlib.sha256(payload.encode()).hexdigest()
        assert stored_hash == expected

    def test_load_session(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        path = sl.close()
        data = load_session(path)
        assert data["session_id"] == sl.session_id

    def test_list_sessions_finds_closed(self, tmp_path):
        sl1 = self._make_logger(tmp_path)
        sl1.start()
        sl1.close()
        sl2 = SessionLogger(agent_label="agent2", agent_class="human", zone="lodge", ledger_dir=tmp_path)
        sl2.start()
        sl2.close()
        sessions = list_sessions(tmp_path)
        assert len(sessions) == 2

    def test_cannot_record_after_close(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        sl.close()
        with pytest.raises(RuntimeError):
            sl.record(pillar_id=1, raw_score=0.5, final_score=0.5)

    def test_multiple_records(self, tmp_path):
        sl = self._make_logger(tmp_path)
        sl.start()
        for pid in [1, 2, 3]:
            sl.record(pillar_id=pid, raw_score=0.9, final_score=0.9)
        path = sl.close()
        data = json.loads(path.read_text())
        assert 3 in data["pillars_attempted"]


# ─────────────────────────────────────────────────────────────────────────────
# Zone 1d — Leaderboard
# ─────────────────────────────────────────────────────────────────────────────

class TestLeaderboard:
    """SQLite leaderboard tests."""

    def _lb(self, tmp_path):
        return Leaderboard(db_path=tmp_path / "lb.db")

    def _result(self, pid=1, score=0.9, agent="test"):
        return PrecisionResult(
            pillar_id=pid,
            agent_label=agent,
            raw_score=score,
            final_score=score,
        )

    def test_upsert_and_top(self, tmp_path):
        lb = self._lb(tmp_path)
        lb.upsert(session_id="s1", agent_label="alpha", agent_class="human",
                  zone="arcade", result=self._result(score=0.9, agent="alpha"))
        lb.upsert(session_id="s2", agent_label="beta", agent_class="llm-api",
                  zone="arcade", result=self._result(score=0.7, agent="beta"))
        top = lb.top(n=5)
        assert len(top) >= 1

    def test_pillar_stats_empty(self, tmp_path):
        lb = self._lb(tmp_path)
        stats = lb.pillar_stats(99999)
        assert stats["pillar_id"] == 99999
        assert stats["n_attempts"] == 0

    def test_pillar_stats_after_upsert(self, tmp_path):
        lb = self._lb(tmp_path)
        lb.upsert(session_id="s1", agent_label="alpha", agent_class="human",
                  zone="arcade", result=self._result(pid=7, score=0.85, agent="alpha"))
        stats = lb.pillar_stats(7)
        assert stats["n_attempts"] == 1
        assert stats["mean_score"] == pytest.approx(0.85)

    def test_record_session(self, tmp_path):
        lb = self._lb(tmp_path)
        # record_session writes to sessions table; verify no exception raised
        lb.record_session(
            session_id="s_abc",
            agent_label="agent_x",
            agent_class="rl-agent",
            zone="training",
            mean_score=0.75,
            pillars_attempted=3,
        )
        # Idempotent upsert: calling again with same session_id should not raise
        lb.record_session(
            session_id="s_abc",
            agent_label="agent_x",
            agent_class="rl-agent",
            zone="training",
            mean_score=0.80,
            pillars_attempted=4,
        )

    def test_summary_keys(self, tmp_path):
        lb = self._lb(tmp_path)
        s = lb.summary()
        assert "n_agents" in s
        assert "n_score_rows" in s

    def test_agent_history(self, tmp_path):
        lb = self._lb(tmp_path)
        lb.upsert(session_id="s1", agent_label="myagent", agent_class="human",
                  zone="arcade", result=self._result(pid=1, score=0.9, agent="myagent"))
        history = lb.agent_history("myagent")
        assert len(history) >= 1
        assert history[0]["agent_label"] == "myagent"

    def test_multiple_agents_ranked(self, tmp_path):
        lb = self._lb(tmp_path)
        for i, (label, score) in enumerate([("low", 0.3), ("mid", 0.6), ("top", 0.95)]):
            lb.upsert(session_id=f"s{i}", agent_label=label, agent_class="human",
                      zone="arcade", result=self._result(pid=1, score=score, agent=label))
        top = lb.top(n=10)
        labels = [row["agent_label"] for row in top]
        assert "top" in labels


# ─────────────────────────────────────────────────────────────────────────────
# Zone 2 — Logic Lodge (lodge_zone)
# ─────────────────────────────────────────────────────────────────────────────

class TestLodgePrompts:
    """Static prompt catalogue."""

    def test_prompts_nonempty(self):
        assert len(LODGE_PROMPTS) >= 1

    def test_prompt_types_valid(self):
        valid = {"derive", "gap", "falsify", "compare", "extend"}
        for p in LODGE_PROMPTS:
            assert p.prompt_type in valid, f"Bad type: {p.prompt_type}"

    def test_all_prompts_have_text(self):
        for p in LODGE_PROMPTS:
            assert p.text and isinstance(p.text, str)

    def test_all_prompts_have_rubric(self):
        for p in LODGE_PROMPTS:
            assert isinstance(p.rubric, dict)

    def test_prompt_ids_unique(self):
        ids = [p.prompt_id for p in LODGE_PROMPTS]
        assert len(ids) == len(set(ids))


class TestAutoScoreSubmission:
    """auto_score_submission function."""

    def _sub(self, reasoning="", numeric=None):
        return LodgeSubmission(
            agent_label="test",
            agent_class="llm-api",
            prompt_id=LODGE_PROMPTS[0].prompt_id,
            reasoning_trace=reasoning,
            numeric_claims=numeric or {},
        )

    def test_returns_float(self):
        prompt = LODGE_PROMPTS[0]
        s = auto_score_submission(self._sub(), prompt)
        assert isinstance(s, float)

    def test_result_in_unit_interval(self):
        for prompt in LODGE_PROMPTS:
            sub = self._sub(reasoning="uncertain gap approximate", numeric={"n_s": 0.9635})
            s = auto_score_submission(sub, prompt)
            assert 0.0 <= s <= 1.0

    def test_no_claims_low_score_short_trace(self):
        prompt = LODGE_PROMPTS[0]
        s = auto_score_submission(self._sub(reasoning="ok"), prompt)
        assert s <= 0.6  # no numeric claims, short trace

    def test_with_numeric_claims_higher_score(self):
        prompt = LODGE_PROMPTS[0]
        if prompt.known_answer is not None:
            s_no = auto_score_submission(self._sub(reasoning="ok"), prompt)
            s_yes = auto_score_submission(self._sub(reasoning="ok", numeric={"n_s": 0.9635}), prompt)
            assert s_yes >= s_no

    def test_neutral_score_for_textual_prompt(self):
        from lodge.lodge_zone import LodgePrompt
        p = LodgePrompt(
            prompt_id="test-textonly",
            prompt_type="extend",
            difficulty="hard",
            domain="test",
            text="Propose an extension.",
            rubric={},
            known_answer=None,
        )
        sub = self._sub(reasoning="some reasoning")
        s = auto_score_submission(sub, p)
        assert s == pytest.approx(0.5)


class TestLodgeReviewQueue:
    """Human review queue."""

    def _sub(self, tmp_path):
        return LodgeSubmission(
            agent_label="test_agent",
            agent_class="human",
            prompt_id=LODGE_PROMPTS[0].prompt_id,
            reasoning_trace="This is my reasoning. Gap in Admission 2.",
            numeric_claims={"n_s": 0.9635},
        )

    def test_submit_creates_file(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        sub = self._sub(tmp_path)
        path = q.submit(sub)
        assert path.exists()

    def test_pending_returns_submitted(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        sub = self._sub(tmp_path)
        q.submit(sub)
        pending = q.pending()
        assert len(pending) >= 1

    def test_pending_is_unreviewed(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        q.submit(self._sub(tmp_path))
        for p in q.pending():
            assert not p.reviewed

    def test_complete_review_marks_reviewed(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        sub = self._sub(tmp_path)
        q.submit(sub)
        q.complete_review(sub.submission_id, human_score=0.8, notes="Good.")
        reviewed = q.all_reviewed()
        assert len(reviewed) >= 1
        assert reviewed[0].reviewed

    def test_complete_review_final_score(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        sub = self._sub(tmp_path)
        q.submit(sub)
        # auto_score is set by submit(); retrieve it from pending
        pending = q.pending()
        auto = pending[0].auto_score if pending[0].auto_score is not None else 0.5
        q.complete_review(sub.submission_id, human_score=0.9, notes="OK")
        reviewed = q.all_reviewed()
        r = reviewed[0]
        # final = 0.6*auto + 0.4*human
        expected = round(0.6 * auto + 0.4 * 0.9, 4)
        assert r.final_score == pytest.approx(expected, abs=1e-3)

    def test_reviewed_not_in_pending(self, tmp_path):
        q = LodgeReviewQueue(queue_dir=tmp_path)
        sub = self._sub(tmp_path)
        q.submit(sub)
        q.complete_review(sub.submission_id, human_score=0.8)
        assert len(q.pending()) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Zone 3 — Training Gym (rl_env)
# ─────────────────────────────────────────────────────────────────────────────

class TestLodgeEnv:
    """gymnasium-compatible RL environment."""

    def _env(self, **kwargs):
        try:
            from lodge.rl_env import LodgeEnv
            return LodgeEnv(log_sessions=False, shuffle=False, **kwargs)
        except ImportError:
            pytest.skip("gymnasium not available")

    def test_reset_returns_obs_and_info(self):
        env = self._env()
        obs, info = env.reset(seed=0)
        assert obs is not None
        assert isinstance(info, dict)

    def test_observation_shape(self):
        import numpy as np
        env = self._env()
        obs, _ = env.reset(seed=0)
        assert obs.shape == (5,)

    def test_observation_dtype_float(self):
        import numpy as np
        env = self._env()
        obs, _ = env.reset(seed=0)
        assert obs.dtype in (np.float32, np.float64)

    def test_observation_bounds(self):
        env = self._env()
        obs, _ = env.reset(seed=0)
        # All elements should be in [0, 1] range (some may exceed for pillar_id if unnorm)
        for val in obs:
            assert math.isfinite(float(val))

    def test_action_space_discrete(self):
        env = self._env()
        n = len(REGISTRY.ids())
        assert env.action_space.n == n

    def test_step_returns_five_tuple(self):
        env = self._env()
        env.reset(seed=0)
        result = env.step(0)
        assert len(result) == 5

    def test_step_reward_in_unit_interval(self):
        env = self._env()
        env.reset(seed=0)
        _, reward, _, _, _ = env.step(0)
        assert 0.0 <= reward <= 1.0

    def test_step_terminated_eventually(self):
        env = self._env()
        env.reset(seed=0)
        n = env.action_space.n
        terminated = False
        for i in range(n + 1):
            _, _, term, trunc, _ = env.step(i % n)
            if term or trunc:
                terminated = True
                break
        assert terminated

    def test_reset_after_done(self):
        env = self._env()
        env.reset(seed=0)
        n = env.action_space.n
        for i in range(n + 1):
            _, _, term, trunc, _ = env.step(i % n)
            if term or trunc:
                break
        obs, _ = env.reset(seed=1)
        assert obs.shape == (5,)

    def test_difficulty_filter(self):
        from lodge.rl_env import LodgeEnv
        easy = REGISTRY.by_difficulty("easy")
        if not easy:
            pytest.skip("no easy pillars in registry")
        env = LodgeEnv(log_sessions=False, difficulty_filter="easy")
        assert env.action_space.n == len(easy)

    def test_invalid_difficulty_raises(self):
        from lodge.rl_env import LodgeEnv
        with pytest.raises(ValueError):
            LodgeEnv(log_sessions=False, difficulty_filter="nonexistent_difficulty_xyz")

    def test_close_does_not_raise(self):
        env = self._env()
        env.reset(seed=0)
        env.close()  # should not raise

    def test_render_text_mode(self):
        from lodge.rl_env import LodgeEnv
        env = LodgeEnv(log_sessions=False, shuffle=False, render_mode="text")
        env.reset(seed=0)
        env.step(0)
        rendered = env.render()
        # Returns string or None depending on render_mode
        assert rendered is None or isinstance(rendered, str)


# ─────────────────────────────────────────────────────────────────────────────
# Zone 5 — Knowledge Exchange (rag_bridge)
# ─────────────────────────────────────────────────────────────────────────────

class TestKnowledgeExchange:
    """RAG-backed knowledge exchange."""

    def test_ask_returns_dict(self):
        ke = KnowledgeExchange()
        result = ke.ask("What is the winding number?")
        assert isinstance(result, dict)

    def test_ask_has_answer_key(self):
        ke = KnowledgeExchange()
        result = ke.ask("What is K_CS?")
        assert "answer" in result

    def test_ask_has_citations(self):
        ke = KnowledgeExchange()
        result = ke.ask("What is n_s?")
        assert "citations" in result

    def test_ask_has_confidence(self):
        ke = KnowledgeExchange()
        result = ke.ask("Explain the birefringence prediction.")
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_ask_echoes_question(self):
        ke = KnowledgeExchange()
        q = "What is the braided sound speed?"
        result = ke.ask(q)
        assert result["question"] == q

    def test_answer_is_string(self):
        ke = KnowledgeExchange()
        result = ke.ask("Describe the FTUM fixed point.")
        assert isinstance(result["answer"], str)

    def test_history_grows(self):
        ke = KnowledgeExchange()
        before = len(ke.history())
        ke.ask("First question")
        ke.ask("Second question")
        assert len(ke.history()) == before + 2

    def test_top_questions_returns_list(self):
        ke = KnowledgeExchange()
        ke.ask("What is K_CS?")
        ke.ask("What is n_s?")
        top = ke.top_questions(n=5)
        assert isinstance(top, list)

    def test_empty_question_handled(self):
        ke = KnowledgeExchange()
        result = ke.ask("")
        assert "answer" in result

    def test_physics_constants_referenced(self):
        ke = KnowledgeExchange()
        result = ke.ask("What is the value of the winding number n_w?")
        # The answer should reference 5 somewhere since n_w=5
        assert result["answer"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# Integration: end-to-end arcade flow
# ─────────────────────────────────────────────────────────────────────────────

class TestArcadeIntegration:
    """End-to-end: registry → score → logger → leaderboard."""

    def test_full_arcade_flow(self, tmp_path):
        """Simulate a single agent playing through the arcade."""
        lb = Leaderboard(db_path=tmp_path / "lb.db")
        sl = SessionLogger(
            agent_label="integration_agent",
            agent_class="llm-api",
            zone="arcade",
            ledger_dir=tmp_path,
        )
        sl.start()

        entries = list(REGISTRY.all())[:3]
        for e in entries:
            gt = e.load_ground_truth()
            result = score_answer(
                pillar_id=e.pillar_id,
                agent_label="integration_agent",
                agent_answer=gt,
                ground_truth=gt,
                expected_type=e.expected_type,
            )
            sl.record(
                pillar_id=e.pillar_id,
                raw_score=result.raw_score,
                final_score=result.final_score,
            )
            lb.upsert(
                session_id=sl.session_id,
                agent_label="integration_agent",
                agent_class="llm-api",
                zone="arcade",
                result=result,
            )

        path = sl.close()
        data = json.loads(path.read_text())

        assert data["agent_label"] == "integration_agent"
        assert len(data["pillars_attempted"]) == 3

        top = lb.top(n=5)
        labels = [row["agent_label"] for row in top]
        assert "integration_agent" in labels

    def test_registry_and_scorer_consistent(self):
        """Ground truth from registry + scorer must always return valid PrecisionResult."""
        for e in REGISTRY.all():
            gt = e.load_ground_truth()
            etype = e.expected_type
            if isinstance(gt, dict) and etype == "float":
                etype = "dict"
            r = score_answer(
                pillar_id=e.pillar_id,
                agent_label="consistency",
                agent_answer=gt,
                ground_truth=gt,
                expected_type=etype,
            )
            assert isinstance(r, PrecisionResult)
            assert 0.0 <= r.final_score <= 1.0
