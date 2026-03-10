from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from llama_index.core import Document, Settings as LlamaSettings, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

from config import get_settings


class MemoryIndexer:
    def __init__(self) -> None:
        self.base_dir: Path | None = None
        self._index: VectorStoreIndex | None = None

    def configure(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self._memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def _memory_path(self) -> Path:
        if self.base_dir is None:
            raise RuntimeError("MemoryIndexer is not configured")
        return self.base_dir / "memory" / "MEMORY.md"

    @property
    def _storage_dir(self) -> Path:
        if self.base_dir is None:
            raise RuntimeError("MemoryIndexer is not configured")
        return self.base_dir / "storage" / "memory_index"

    @property
    def _meta_path(self) -> Path:
        return self._storage_dir / "meta.json"

    def _supports_embeddings(self) -> bool:
        return bool(get_settings().embedding_api_key)

    def _build_embed_model(self) -> OpenAIEmbedding:
        settings = get_settings()
        return OpenAIEmbedding(
            api_key=settings.embedding_api_key,
            api_base=settings.embedding_base_url,
            model=settings.embedding_model,
        )

    def _file_digest(self) -> str:
        if not self._memory_path.exists():
            return ""
        return hashlib.md5(self._memory_path.read_bytes()).hexdigest()

    def _read_meta(self) -> dict[str, Any]:
        if not self._meta_path.exists():
            return {}
        try:
            return json.loads(self._meta_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_meta(self, digest: str) -> None:
        self._meta_path.write_text(
            json.dumps({"digest": digest}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def rebuild_index(self) -> None:
        if self.base_dir is None:
            return

        if not self._memory_path.exists():
            self._memory_path.write_text("# Long-term Memory\n\n", encoding="utf-8")

        digest = self._file_digest()
        self._write_meta(digest)

        if not self._supports_embeddings():
            self._index = None
            return

        try:
            LlamaSettings.embed_model = self._build_embed_model()
            content = self._memory_path.read_text(encoding="utf-8").strip()
            splitter = SentenceSplitter(chunk_size=256, chunk_overlap=32)
            documents = [Document(text=content, metadata={"source": "memory/MEMORY.md"})]
            nodes = splitter.get_nodes_from_documents(documents)
            self._index = VectorStoreIndex(nodes)
            self._index.storage_context.persist(persist_dir=str(self._storage_dir))
        except Exception:
            self._index = None

    def _load_index(self) -> None:
        if not self._supports_embeddings():
            self._index = None
            return
        persisted_files = [
            path for path in self._storage_dir.iterdir() if path.name not in {".gitkeep", "meta.json"}
        ]
        if not persisted_files:
            self.rebuild_index()
            return
        try:
            LlamaSettings.embed_model = self._build_embed_model()
            storage_context = StorageContext.from_defaults(persist_dir=str(self._storage_dir))
            self._index = load_index_from_storage(storage_context)
        except Exception:
            self._index = None

    def _maybe_rebuild(self) -> None:
        if self.base_dir is None:
            return
        digest = self._file_digest()
        if digest != self._read_meta().get("digest"):
            self.rebuild_index()
            return
        if self._index is None and self._supports_embeddings():
            self._load_index()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if self.base_dir is None:
            return []

        self._maybe_rebuild()
        if self._index is None:
            return []

        retriever = self._index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
        payload: list[dict[str, Any]] = []
        for item in results:
            node = getattr(item, "node", item)
            text = getattr(node, "text", "") or getattr(node, "get_content", lambda: "")()
            payload.append(
                {
                    "text": text,
                    "score": float(getattr(item, "score", 0.0) or 0.0),
                    "source": node.metadata.get("source", "memory/MEMORY.md"),
                }
            )
        return payload


memory_indexer = MemoryIndexer()
