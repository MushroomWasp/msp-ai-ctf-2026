from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    doc_id: str
    doc_title: str
    chunk_id: int
    content: str
    is_protected: bool = False


class SemanticVectorStore:
    """A semantic vector database using term-frequency and subword n-gram cosine similarity."""

    def __init__(self) -> None:
        self.chunks: list[DocumentChunk] = []

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        words = re.findall(r"\b[a-z0-9_-]{2,}\b", text)
        ngrams = []
        for word in words:
            if len(word) >= 3:
                for i in range(len(word) - 2):
                    ngrams.append(f"__3g_{word[i:i+3]}")
            if len(word) >= 4:
                for i in range(len(word) - 3):
                    ngrams.append(f"__4g_{word[i:i+4]}")
        return words + ngrams

    def _to_vector(self, tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        total = len(tokens) or 1
        return {term: count / total for term, count in tf.items()}

    def _cosine_similarity(self, vec1: dict[str, float], vec2: dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        if not intersection:
            return 0.0
        dot_product = sum(vec1[x] * vec2[x] for x in intersection)
        mag1 = math.sqrt(sum(val * val for val in vec1.values()))
        mag2 = math.sqrt(sum(val * val for val in vec2.values()))
        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def add_document(self, doc_id: str, title: str, content: str, is_protected: bool = False) -> None:
        self.chunks.append(
            DocumentChunk(
                doc_id=doc_id,
                doc_title=title,
                chunk_id=1,
                content=content.strip(),
                is_protected=is_protected,
            )
        )

    def remove_document(self, doc_id: str) -> None:
        self.chunks = [c for c in self.chunks if c.doc_id != doc_id]

    def search(self, query: str, top_k: int = 2, min_score: float = 0.04) -> list[tuple[DocumentChunk, float]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
        query_vec = self._to_vector(query_tokens)

        scored: list[tuple[DocumentChunk, float]] = []
        for chunk in self.chunks:
            chunk_tokens = self._tokenize(chunk.content + " " + chunk.doc_title)
            chunk_vec = self._to_vector(chunk_tokens)
            score = self._cosine_similarity(query_vec, chunk_vec)
            if score >= min_score:
                scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
