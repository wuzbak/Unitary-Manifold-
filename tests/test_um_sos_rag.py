from pathlib import Path

from src.core.um_sos_rag import answer_with_labels, build_chunks

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_rag_answer_contains_label():
    base = REPO_ROOT / "docs"
    chunks = build_chunks([base / "CLAIM_MASTER_BOARD.md", base / "GATEKEEPER_SUMMARY.md"])
    out = answer_with_labels("What is the current dark energy tension?", chunks)
    assert out["epistemic_label"] in {"DERIVED", "CONSTRAINED", "ARCHITECTURE_LIMIT"}
    assert out["source"]
