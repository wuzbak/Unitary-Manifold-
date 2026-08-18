"""
TerraOS — Bot Tests (34)
"""
from __future__ import annotations
import pytest


# ---- TF-IDF internals ----
def test_tokenize_basic():
    from terra.app.bot.terra_bot import _tokenize
    tokens = _tokenize("clay soil pH loam")
    assert "clay" in tokens
    assert "soil" in tokens


def test_tokenize_lowercase():
    from terra.app.bot.terra_bot import _tokenize
    tokens = _tokenize("Sandy LOAM")
    assert "sandy" in tokens
    assert "loam" in tokens


def test_tokenize_min_length():
    from terra.app.bot.terra_bot import _tokenize
    tokens = _tokenize("pH is 7")
    assert all(len(t) >= 3 for t in tokens)


def test_split_paragraphs_basic():
    from terra.app.bot.terra_bot import _split_paragraphs
    text = "This is a test of soil science.\n\nAnother paragraph about water quality."
    chunks = _split_paragraphs(text)
    assert len(chunks) >= 1


def test_split_paragraphs_max_tokens():
    from terra.app.bot.terra_bot import _split_paragraphs
    text = " ".join(["word"] * 400)
    chunks = _split_paragraphs(text, max_tokens=180)
    assert len(chunks) >= 2


def test_split_paragraphs_empty():
    from terra.app.bot.terra_bot import _split_paragraphs
    chunks = _split_paragraphs("")
    assert chunks == []


def test_idf_computation():
    from terra.app.bot.terra_bot import _idf
    corpus = [["soil", "clay"], ["water", "ph", "soil"], ["clay", "silt"]]
    idf = _idf(corpus)
    assert "soil" in idf
    assert idf["ph"] > idf["soil"]


def test_idf_rare_terms_higher():
    from terra.app.bot.terra_bot import _idf
    corpus = [["common", "rare"], ["common", "other"], ["common", "more"]]
    idf = _idf(corpus)
    assert idf["rare"] > idf["common"]


def test_score_returns_float():
    from terra.app.bot.terra_bot import _score, _idf
    q = ["soil", "clay"]
    doc = ["soil", "texture", "clay", "loam"]
    idf = _idf([q, doc])
    s = _score(q, doc, idf)
    assert isinstance(s, float)
    assert s >= 0


def test_score_zero_for_no_overlap():
    from terra.app.bot.terra_bot import _score, _idf
    q = ["xyzzy", "nothere"]
    doc = ["soil", "clay", "loam"]
    corpus = [q, doc]
    idf = _idf(corpus)
    s = _score(q, doc, idf)
    assert s == 0.0


def test_build_chunks_returns_list():
    from terra.app.bot.terra_bot import _build_chunks
    chunks = _build_chunks()
    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_retrieve_returns_list():
    from terra.app.bot.terra_bot import retrieve
    chunks = retrieve("soil pH")
    assert isinstance(chunks, list)


def test_retrieve_top_k():
    from terra.app.bot.terra_bot import retrieve
    chunks = retrieve("clay soil drainage", top_k=2)
    assert len(chunks) <= 2


def test_retrieve_empty_query():
    from terra.app.bot.terra_bot import retrieve
    chunks = retrieve("")
    assert isinstance(chunks, list)


def test_retrieve_unknown_query():
    from terra.app.bot.terra_bot import retrieve
    chunks = retrieve("xyznonsensexyz")
    assert isinstance(chunks, list)


# ---- TerraBot class ----
def test_terra_bot_init():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    assert bot is not None


def test_terra_bot_ask_returns_string():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    answer = bot.ask("What is clay soil?")
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_terra_bot_ask_soil_ph():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    answer = bot.ask("What is the optimal soil pH for vegetables?")
    assert isinstance(answer, str)


def test_terra_bot_ask_water_quality():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    answer = bot.ask("Is river water safe to drink?")
    assert isinstance(answer, str)


def test_terra_bot_ask_empty():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    answer = bot.ask("")
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_terra_bot_ask_amendment():
    from terra.app.bot.terra_bot import TerraBot
    bot = TerraBot()
    answer = bot.ask("Should I add compost to sandy soil?")
    assert isinstance(answer, str)


# ---- TerraGovernor / Agents ----
def test_governor_init():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    assert gov is not None


def test_governor_respond_returns_result():
    from terra.app.bot.agents import TerraGovernor, GovernorResult
    gov = TerraGovernor()
    result = gov.respond("What is the pH of clay soil?")
    assert isinstance(result, GovernorResult)


def test_governor_respond_soil_question():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("What soil texture is best for root vegetables?")
    assert result.agent_name in ["SoilAnalyst", "AgronomistAdvisor"]


def test_governor_respond_water_question():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("What is the TDS of drinking water?")
    assert result.agent_name == "WaterChemist"


def test_governor_respond_remediation_question():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("How to remediate lead contamination in soil?")
    assert result.agent_name == "RemediationOfficer"


def test_governor_respond_agronomy_question():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("What crops grow best in sandy loam?")
    assert result.agent_name in ["AgronomistAdvisor", "SoilAnalyst"]


def test_governor_respond_ecology_question():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("How do wetland ecosystems filter water?")
    assert result.agent_name in ["EcologyGuide", "WaterChemist"]


def test_governor_result_has_answer():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("Explain soil drainage")
    assert len(result.answer) > 0


def test_governor_result_context_chunks():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("soil pH amendment lime")
    assert isinstance(result.context_chunks, list)


def test_governor_result_confidence():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("clay soil waterlogging")
    assert 0.0 <= result.confidence <= 1.0


def test_agent_overlays_have_five():
    from terra.app.bot.agents import AGENT_OVERLAYS
    assert len(AGENT_OVERLAYS) == 5


def test_all_agent_names_present():
    from terra.app.bot.agents import AGENT_OVERLAYS
    expected = {"SoilAnalyst", "WaterChemist", "AgronomistAdvisor", "EcologyGuide", "RemediationOfficer"}
    assert set(AGENT_OVERLAYS.keys()) == expected


def test_governor_classify_contamination_intent():
    from terra.app.bot.agents import TerraGovernor
    gov = TerraGovernor()
    result = gov.respond("What is the arsenic threshold for soil remediation?")
    assert result.agent_name == "RemediationOfficer"
