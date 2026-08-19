"""
LithosOS — Bot Tests (34 tests)
"""
from __future__ import annotations
import pytest

class TestTokenize:
    def test_basic(self):
        from lithic.app.bot.lithos_bot import _tokenize
        tokens = _tokenize("quartz mineral silicon")
        assert "quartz" in tokens
        assert "mineral" in tokens

    def test_case_insensitive(self):
        from lithic.app.bot.lithos_bot import _tokenize
        tokens = _tokenize("Quartz MINERAL Silicon")
        assert "quartz" in tokens
        assert "mineral" in tokens

    def test_handles_empty(self):
        from lithic.app.bot.lithos_bot import _tokenize
        assert _tokenize("") == []

    def test_handles_special_chars(self):
        from lithic.app.bot.lithos_bot import _tokenize
        tokens = _tokenize("Fe2O3 SiO2 composition")
        assert "fe2o3" in tokens or "fe" in tokens or "sio2" in tokens or "composition" in tokens

class TestSplitParagraphs:
    def test_basic_split(self):
        from lithic.app.bot.lithos_bot import _split_paragraphs
        text = "Paragraph one about quartz.\n\nParagraph two about feldspar."
        chunks = _split_paragraphs(text)
        assert len(chunks) >= 1
        assert any("quartz" in c for c in chunks)

    def test_merges_short_paras(self):
        from lithic.app.bot.lithos_bot import _split_paragraphs
        text = "Short.\n\nAlso short.\n\nStill short."
        chunks = _split_paragraphs(text)
        assert len(chunks) >= 1

    def test_handles_empty(self):
        from lithic.app.bot.lithos_bot import _split_paragraphs
        assert _split_paragraphs("") == []

    def test_long_paragraph_is_one_chunk(self):
        from lithic.app.bot.lithos_bot import _split_paragraphs
        long_text = "x" * 500
        chunks = _split_paragraphs(long_text)
        assert len(chunks) == 1

class TestRetrieve:
    def test_retrieves_relevant_chunk(self):
        from lithic.app.bot.lithos_bot import _build_chunks, _idf, retrieve
        docs = [{"filename": "test.md", "text": "Quartz is SiO2 with Mohs hardness 7.\n\nDiamond is the hardest mineral."}]
        chunks = _build_chunks(docs)
        idf = _idf(chunks)
        results = retrieve("quartz hardness", chunks, idf)
        assert len(results) > 0

    def test_returns_top_k(self):
        from lithic.app.bot.lithos_bot import _build_chunks, _idf, retrieve
        docs = [{"filename": "a.md", "text": "Gold is a metal.\n\nSilver is also a metal.\n\nCopper is a metal."}]
        chunks = _build_chunks(docs)
        idf = _idf(chunks)
        results = retrieve("metal", chunks, idf, top_k=2)
        assert len(results) <= 2

    def test_handles_empty_chunks(self):
        from lithic.app.bot.lithos_bot import retrieve
        results = retrieve("quartz", [], {})
        assert results == []

    def test_returns_nothing_for_no_match(self):
        from lithic.app.bot.lithos_bot import _build_chunks, _idf, retrieve
        docs = [{"filename": "a.md", "text": "Quartz is a mineral."}]
        chunks = _build_chunks(docs)
        idf = _idf(chunks)
        results = retrieve("", chunks, idf)
        assert results == []

class TestLithosBotOffline:
    def test_chunks_loaded(self):
        from lithic.app.bot.lithos_bot import LithosBot
        bot = LithosBot()
        assert isinstance(bot._chunks, list)

    def test_offline_fallback(self):
        from lithic.app.bot.lithos_bot import LithosBot
        bot = LithosBot(api_key="", local_llm_url="http://localhost:0/")
        answer = bot.ask("What is the Mohs hardness of quartz?")
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_build_messages(self):
        from lithic.app.bot.lithos_bot import LithosBot
        bot = LithosBot()
        msgs = bot._build_messages("Tell me about pyrite")
        assert isinstance(msgs, list)
        assert msgs[0]["role"] == "system"
        assert msgs[-1]["role"] == "user"

    def test_extra_context(self):
        from lithic.app.bot.lithos_bot import LithosBot
        bot = LithosBot()
        msgs = bot._build_messages("What is pyrite?", context="Iron sulfide", extra_system="ROLE: Specialist")
        assert any("ROLE: Specialist" in m["content"] for m in msgs)

class TestGovernor:
    def test_classify_identifier_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        assert gov._classify_intent("identify this specimen") == "Identifier"

    def test_classify_geologist_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        assert gov._classify_intent("what crystal system is quartz") == "Geologist"

    def test_classify_lapidary_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        assert gov._classify_intent("how do I polish a cabochon") == "Lapidary"

    def test_classify_metallurgist_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        assert gov._classify_intent("what are the ores for copper smelting") == "Metallurgist"

    def test_classify_market_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        assert gov._classify_intent("what is the price per carat for emerald") == "MarketGuide"

    def test_default_intent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        result = gov._classify_intent("tell me something interesting")
        assert result in ["Geologist", "Identifier", "Lapidary", "Metallurgist", "MarketGuide"]

    def test_valid_agent_names(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        for name in ["Identifier", "Geologist", "Lapidary", "Metallurgist", "MarketGuide"]:
            agent = gov.agent(name)
            assert agent.name == name

    def test_unknown_agent_raises(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        with pytest.raises(KeyError):
            gov.agent("Nonexistent")

    def test_route_returns_result(self):
        from lithic.app.bot.agents import LithosGovernor, GovernorResult
        gov = LithosGovernor()
        result = gov.route("What is the hardness of diamond?")
        assert isinstance(result, GovernorResult)
        assert result.answer

    def test_route_uses_correct_agent(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        result = gov.route("How do I cut a cabochon?")
        assert "Lapidary" in result.agents_used

    def test_ask_agent_direct(self):
        from lithic.app.bot.agents import LithosGovernor
        gov = LithosGovernor()
        answer = gov.ask_agent("Geologist", "What is the crystal system of quartz?")
        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_governor_result_str(self):
        from lithic.app.bot.agents import GovernorResult
        result = GovernorResult(query="test", agents_used=["Geologist"], answer="Quartz is trigonal.")
        s = str(result)
        assert "Geologist" in s

class TestGibberBridge:
    def test_encode_decode_payload(self):
        from lithic.app.sync.gibberlink_bridge import GibberPayload, PayloadType
        p = GibberPayload(payload_type=PayloadType.SPECIMEN_ID, data={"name": "Quartz", "confidence": 0.9})
        encoded = p.encode()
        decoded = GibberPayload.decode(encoded)
        assert decoded.payload_type == PayloadType.SPECIMEN_ID
        assert decoded.data["name"] == "Quartz"

    def test_hmac_sign_verify(self):
        from lithic.app.sync.gibberlink_bridge import AcousticAuth
        auth = AcousticAuth("test-secret")
        sig = auth.sign("hello")
        assert auth.verify("hello", sig)

    def test_hmac_verify_fails_tampered(self):
        from lithic.app.sync.gibberlink_bridge import AcousticAuth
        auth = AcousticAuth("test-secret")
        sig = auth.sign("hello")
        assert not auth.verify("world", sig)

    def test_mode_settings(self):
        from lithic.app.sync.gibberlink_bridge import GibberBridge, GibberMode
        bridge = GibberBridge(mode=GibberMode.RED)
        assert bridge._mode == GibberMode.RED

    def test_broadcast_returns_bool(self):
        from lithic.app.sync.gibberlink_bridge import GibberBridge, GibberMode
        bridge = GibberBridge(enabled=False)
        result = bridge.broadcast_specimen_id("Gold", 0.9, GibberMode.GREEN)
        assert isinstance(result, bool)
        assert result is False

    def test_payload_types(self):
        from lithic.app.sync.gibberlink_bridge import PayloadType
        assert PayloadType.SPECIMEN_ID == "SID"
        assert PayloadType.QUERY == "QRY"
        assert PayloadType.PING == "PNG"
