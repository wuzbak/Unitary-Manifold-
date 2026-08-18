"""
LithosOS — RAG Bot
"""
from __future__ import annotations

import math
import re
from pathlib import Path

LITHIC_DIR = Path(__file__).parent.parent.parent

LITHOS_DOCS_ORDERED = [
    "docs/CRYSTAL_SYSTEMS.md",
    "docs/MOHS_SCALE.md",
    "docs/GEMSTONE_GRADING.md",
    "docs/METAL_PROPERTIES.md",
    "docs/LAPIDARY_GUIDE.md",
    "docs/MINING_ETHICS.md",
    "docs/HAZARD_GUIDE.md",
]

LITHOS_SYSTEM_PROMPT = """You are LithosOS — a mineral, gemstone, and metallurgy expert system.

Your knowledge covers: all mineral classes (silicates, oxides, sulfides, carbonates, phosphates,
halides, native elements), gemology and grading, lapidary arts, metallurgy, mining ethics,
and hazardous mineral handling.

AXIOMS:
1. ACCURACY: Every mineralogical claim is based on established crystallography, chemistry, or gemmology.
2. SAFETY FIRST: Always flag toxic minerals (asbestos, cinnabar, malachite dust, arsenic ores).
3. IDENTIFICATION: Give confidence level and distinguish look-alikes. Never say "definitely" from one feature.
4. OFFLINE CAPABLE: Reason from embedded knowledge when no internet is available.

RESPONSE FORMAT:
- Lead with the most relevant fact (identification, composition, or hazard)
- For IDs: give Mohs hardness, crystal system, luster, streak, specific gravity
- For gemstones: include grading criteria (4C equivalents), treatments, synthetic availability
- For metals: include melting point, conductivity, principal ores, industrial uses
- Be precise and technical.
"""

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z][a-z0-9]*", text)
    stopwords = {"the", "a", "an", "is", "in", "of", "and", "or", "to", "for",
                 "with", "it", "as", "at", "by", "on", "be", "are", "was",
                 "this", "that", "has", "have", "not", "from", "its", "been"}
    return [t for t in tokens if t not in stopwords and len(t) > 1]

def _split_paragraphs(text: str, max_chars: int = 1800) -> list[str]:
    raw = re.split(r"\n{2,}", text.strip())
    chunks: list[str] = []
    current = ""
    for para in raw:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            current = para[:max_chars]
    if current:
        chunks.append(current)
    return chunks or [text[:max_chars]] if text.strip() else []

def _build_chunks(docs: list[dict]) -> list[dict]:
    chunks = []
    for doc in docs:
        for para in _split_paragraphs(doc["text"]):
            chunks.append({"source": doc["filename"], "text": para, "tokens": _tokenize(para)})
    return chunks

def _idf(chunks: list[dict]) -> dict[str, float]:
    N = len(chunks)
    df: dict[str, int] = {}
    for chunk in chunks:
        for tok in set(chunk["tokens"]):
            df[tok] = df.get(tok, 0) + 1
    return {tok: math.log((N + 1) / (count + 1)) + 1 for tok, count in df.items()}

def _score(query_tokens: list[str], chunk_tokens: list[str], idf_map: dict[str, float]) -> float:
    tf: dict[str, int] = {}
    for t in chunk_tokens:
        tf[t] = tf.get(t, 0) + 1
    return sum(tf.get(t, 0) * idf_map.get(t, 0) for t in query_tokens)

def retrieve(query: str, chunks: list[dict], idf_map: dict[str, float], top_k: int = 3) -> list[dict]:
    if not chunks:
        return []
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    scored = [(c, _score(q_tokens, c["tokens"], idf_map)) for c in chunks]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, s in scored[:top_k] if s > 0]


class LithosBot:
    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini",
                 local_llm_url: str = "", local_llm_model: str = "llama3.2:3b"):
        self._api_key = api_key
        self._model = model
        self._local_llm_url = local_llm_url
        self._local_llm_model = local_llm_model
        self._docs = self._load_docs()
        self._chunks = _build_chunks(self._docs)
        self._idf = _idf(self._chunks)

    def _load_docs(self) -> list[dict]:
        docs = []
        for rel in LITHOS_DOCS_ORDERED:
            fpath = LITHIC_DIR / rel
            if fpath.exists():
                try:
                    docs.append({"filename": rel, "text": fpath.read_text(encoding="utf-8")})
                except Exception:
                    pass
        return docs

    def _build_messages(self, question: str, context: str = "", extra_system: str = "") -> list[dict]:
        system = LITHOS_SYSTEM_PROMPT
        if extra_system:
            system = extra_system + "\n\n" + system
        relevant = retrieve(question, self._chunks, self._idf)
        rag_ctx = "\n\n---\n\n".join(c["text"] for c in relevant)
        user_content = question
        if rag_ctx:
            user_content = f"[Knowledge base excerpt]\n{rag_ctx}\n\n[Question]\n{question}"
        if context:
            user_content = f"[Context]\n{context}\n\n{user_content}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]

    def ask(self, question: str, context: str = "", extra_system: str = "") -> str:
        if self._api_key:
            return self._ask_openai(question, context, extra_system)
        return self._ask_local(question, context, extra_system)

    def _ask_openai(self, question: str, context: str = "", extra_system: str = "") -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self._api_key)
            messages = self._build_messages(question, context, extra_system)
            resp = client.chat.completions.create(model=self._model, messages=messages, max_tokens=1024)
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"⚠️ OpenAI error: {e}\n\n{self._offline_answer(question)}"

    def _ask_local(self, question: str, context: str = "", extra_system: str = "") -> str:
        try:
            import urllib.request, json as jsonlib
            messages = self._build_messages(question, context, extra_system)
            payload = jsonlib.dumps({
                "model": self._local_llm_model,
                "messages": messages,
                "stream": False,
            }).encode()
            req = urllib.request.Request(
                self._local_llm_url.replace("/generate", "/chat"),
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                data = jsonlib.loads(r.read())
                return data.get("message", {}).get("content", "") or data.get("response", "")
        except Exception as e:
            return f"⚠️ Local LLM error: {e}\n\n{self._offline_answer(question)}"

    def _offline_answer(self, question: str) -> str:
        relevant = retrieve(question, self._chunks, self._idf)
        if not relevant:
            return "No relevant mineral knowledge found in the local knowledge base."
        parts = [f"[From {c['source']}]\n{c['text']}" for c in relevant]
        return "\n\n---\n\n".join(parts)
