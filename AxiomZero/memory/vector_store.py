# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
AxiomZero memory/vector_store.py — ChromaDB / Qdrant vector store interface

Handles:
- Initial corpus indexing (on first boot)
- Incremental updates (git diff since last index)
- Query API used by M5 RAG Manager

Gracefully degrades if ChromaDB is not installed.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import chromadb  # type: ignore
    _CHROMA = True
except ImportError:
    _CHROMA = False

# Default chunk parameters
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64
COLLECTION_NAME = "unitary_manifold"


class VectorStore:
    """
    Unified interface over ChromaDB (local or HTTP).

    Usage::

        vs = VectorStore.from_config()
        vs.index_corpus()      # First boot
        vs.update_incremental() # Subsequent boots
        results = vs.query("5D metric ansatz winding number", n_results=5)
    """

    def __init__(
        self,
        repo_root: Path,
        vectordb_url: str = "local",
        collection_name: str = COLLECTION_NAME,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.repo_root = repo_root
        self.vectordb_url = vectordb_url
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None
        self._index_manifest: Dict[str, str] = {}  # path → sha256 of last indexed version

    @classmethod
    def from_config(cls, config_path: Optional[Path] = None) -> "VectorStore":
        config_path = config_path or (Path.home() / ".axiomzero" / "config.json")
        if config_path.exists():
            cfg = json.loads(config_path.read_text())
        else:
            cfg = {}
        repo_root_str = cfg.get("repo_root")
        repo_root = Path(repo_root_str) if repo_root_str else Path(__file__).parent.parent.parent
        rag_cfg = cfg.get("rag", {})
        return cls(
            repo_root=repo_root,
            vectordb_url=cfg.get("vectordb_url", "local"),
            collection_name=rag_cfg.get("collection_name", COLLECTION_NAME),
            chunk_size=rag_cfg.get("chunk_size", DEFAULT_CHUNK_SIZE),
            chunk_overlap=rag_cfg.get("chunk_overlap", DEFAULT_CHUNK_OVERLAP),
        )

    def connect(self) -> bool:
        """Connect to ChromaDB.  Returns True if successful."""
        if not _CHROMA:
            logger.warning("chromadb not installed — vector store unavailable")
            return False
        try:
            if self.vectordb_url.startswith("http"):
                parts = self.vectordb_url.replace("http://", "").split(":")
                host = parts[0]
                port = int(parts[1]) if len(parts) > 1 else 8001
                self._client = chromadb.HttpClient(host=host, port=port)
            elif self.vectordb_url.startswith("local:"):
                persist_dir = self.vectordb_url.split("local:")[1]
                self._client = chromadb.PersistentClient(path=persist_dir)
            else:
                az_dir = Path.home() / ".axiomzero" / "chroma_data"
                az_dir.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(path=str(az_dir))

            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Connected to ChromaDB collection '%s'", self.collection_name)
            return True
        except Exception as exc:
            logger.error("ChromaDB connection failed: %s", exc)
            return False

    def index_corpus(
        self,
        index_paths: Optional[List[str]] = None,
        progress_cb=None,
    ) -> Dict:
        """
        Full initial indexing pass over the repository corpus.
        Safe to call repeatedly (idempotent via content hashing).
        """
        if not self.connect():
            return {"indexed": 0, "error": "ChromaDB unavailable"}

        default_paths = [
            "src/", "tests/", "recycling/",
            "proof/", "6-MONOGRAPH/", "FALLIBILITY.md",
            "docs/CLAIM_MASTER_BOARD.md", "bot/",
        ]
        paths = index_paths or default_paths

        total_indexed = 0
        total_skipped = 0

        for rel_path in paths:
            full = self.repo_root / rel_path
            if not full.exists():
                continue
            files = [full] if full.is_file() else list(full.rglob("*.py")) + list(full.rglob("*.md"))
            for file_path in files:
                try:
                    result = self._index_file(file_path)
                    if result == "indexed":
                        total_indexed += 1
                        if progress_cb:
                            progress_cb(file_path)
                    else:
                        total_skipped += 1
                except Exception as exc:
                    logger.debug("Failed to index %s: %s", file_path, exc)

        # Save manifest
        self._save_manifest()

        return {
            "indexed": total_indexed,
            "skipped": total_skipped,
            "collection": self.collection_name,
        }

    def update_incremental(self) -> Dict:
        """
        Update index for files changed since last indexing (via git diff).
        Called on subsequent boots.
        """
        changed = self._get_changed_files()
        if not changed:
            return {"updated": 0, "note": "No changes since last index"}

        if not self.connect():
            return {"updated": 0, "error": "ChromaDB unavailable"}

        updated = 0
        for rel_path in changed:
            full = self.repo_root / rel_path
            if full.exists() and full.suffix in (".py", ".md"):
                try:
                    self._index_file(full)
                    updated += 1
                except Exception as exc:
                    logger.debug("Incremental index failed for %s: %s", full, exc)

        self._save_manifest()
        return {"updated": updated, "changed_files": changed}

    def query(self, text: str, n_results: int = 5) -> List[Dict]:
        """Query the vector store for relevant chunks."""
        if not self.connect():
            return []
        try:
            results = self._collection.query(query_texts=[text], n_results=n_results)
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [
                {"text": doc, "source": meta.get("source", ""), "score": None}
                for doc, meta in zip(docs, metas)
            ]
        except Exception as exc:
            logger.error("Vector query failed: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _index_file(self, file_path: Path) -> str:
        """Index a single file.  Returns 'indexed' or 'skipped' (unchanged)."""
        content = file_path.read_text(errors="replace")
        sha = hashlib.sha256(content.encode()).hexdigest()
        rel = str(file_path.relative_to(self.repo_root))

        if self._index_manifest.get(rel) == sha:
            return "skipped"  # Content unchanged

        chunks = self._chunk(content)
        if not chunks:
            return "skipped"

        ids = [f"{rel}::{i}::{sha[:8]}" for i in range(len(chunks))]
        metas = [{"source": rel, "chunk": i} for i in range(len(chunks))]

        # Upsert (handles both new and updated files)
        self._collection.upsert(documents=chunks, ids=ids, metadatas=metas)
        self._index_manifest[rel] = sha
        return "indexed"

    def _chunk(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return [c for c in chunks if c.strip()]

    def _get_changed_files(self) -> List[str]:
        """Get list of files changed since last index via git diff."""
        manifest_path = Path.home() / ".axiomzero" / "index_manifest.json"
        if not manifest_path.exists():
            return []  # No manifest → need full index
        self._index_manifest = json.loads(manifest_path.read_text())

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, cwd=str(self.repo_root), timeout=15
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.splitlines() if f.strip()]
        except Exception:
            pass
        return []

    def _save_manifest(self) -> None:
        """Persist the index manifest to disk."""
        manifest_path = Path.home() / ".axiomzero" / "index_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(self._index_manifest, indent=2))

    def _grep_corpus(self, query: str, max_results: int = 3) -> List[str]:
        """Simple keyword grep over key corpus files (no ChromaDB required)."""
        terms = query.lower().split()[:3]
        hits = []
        corpus_dirs = [
            self.repo_root / "proof",
            self.repo_root / "6-MONOGRAPH",
            self.repo_root / "src" / "core",
        ]
        for d in corpus_dirs:
            if not d.exists():
                continue
            for f in list(d.rglob("*.md"))[:20] + list(d.rglob("*.py"))[:20]:
                try:
                    content = f.read_text(errors="replace")
                    if any(t in content.lower() for t in terms):
                        hits.append(f"[{f.name}] {content[:300]}")
                        if len(hits) >= max_results:
                            return hits
                except Exception:
                    pass
        return hits
