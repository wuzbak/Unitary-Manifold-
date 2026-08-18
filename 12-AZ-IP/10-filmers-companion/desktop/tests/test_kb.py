"""Tests for KB module — 15 tests."""
import pytest


def test_kb_entries_minimum_count():
    from desktop.app.kb.film_kb import KB_ENTRIES
    assert len(KB_ENTRIES) >= 18


def test_kb_entries_have_required_keys():
    from desktop.app.kb.film_kb import KB_ENTRIES
    for entry in KB_ENTRIES:
        assert "keyword" in entry
        assert "content" in entry


def test_search_kb_turnaround():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("turnaround")
    assert len(results) >= 1
    assert any("12" in r["content"] for r in results)


def test_search_kb_budget():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("budget contingency")
    assert len(results) >= 1


def test_search_kb_location_scout():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("location scout")
    assert len(results) >= 1


def test_search_kb_empty_query():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("")
    assert isinstance(results, list)


def test_axiom_omega_principles_count():
    from desktop.app.kb.film_kb import AXIOM_OMEGA_PRINCIPLES
    assert len(AXIOM_OMEGA_PRINCIPLES) >= 10


def test_feedback_loop_metrics_count():
    from desktop.app.kb.film_kb import FEEDBACK_LOOP_METRICS
    assert len(FEEDBACK_LOOP_METRICS) >= 6


def test_budget_allocation_defaults_count():
    from desktop.app.kb.film_kb import BUDGET_ALLOCATION_DEFAULTS
    assert len(BUDGET_ALLOCATION_DEFAULTS) >= 10


def test_budget_allocation_sums_to_100():
    from desktop.app.kb.film_kb import BUDGET_ALLOCATION_DEFAULTS
    total = sum(v["pct"] for v in BUDGET_ALLOCATION_DEFAULTS.values())
    assert abs(total - 100.0) < 0.01


def test_guild_minimums_has_sag():
    from desktop.app.kb.film_kb import GUILD_MINIMUMS
    assert "SAG" in GUILD_MINIMUMS or any("SAG" in k for k in GUILD_MINIMUMS)


def test_guild_minimums_has_dga():
    from desktop.app.kb.film_kb import GUILD_MINIMUMS
    assert "DGA" in GUILD_MINIMUMS or any("DGA" in k for k in GUILD_MINIMUMS)


def test_search_kb_returns_list_of_dicts():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("call sheet")
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0], dict)


def test_search_kb_case_insensitive():
    from desktop.app.kb.film_kb import search_kb
    lower = search_kb("turnaround")
    upper = search_kb("TURNAROUND")
    assert len(lower) == len(upper)


def test_search_kb_f_stop():
    from desktop.app.kb.film_kb import search_kb
    results = search_kb("f-stop")
    assert len(results) >= 1
