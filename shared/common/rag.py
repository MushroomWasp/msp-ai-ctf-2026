from __future__ import annotations

import math
import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable


TOKEN_RE = re.compile(r"[a-zA-Z0-9]{2,}")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def chunk_text(text: str, *, chunk_words: int = 120, overlap: int = 20) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        chunk = words[start : start + chunk_words]
        chunks.append(" ".join(chunk))
        if start + chunk_words >= len(words):
            break
        start += max(chunk_words - overlap, 1)
    return chunks or [text]


def embed_text(text: str, *, dims: int = 128) -> list[float]:
    vector = [0.0] * dims
    tokens = tokenize(text)
    if not tokens:
        return vector
    for token in tokens:
        digest = sha256(token.encode("utf-8")).digest()
        index = digest[0] % dims
        sign = 1.0 if digest[1] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


@dataclass(slots=True)
class RagChunk:
    doc_id: str
    source: str
    trust: str
    text: str
    embedding: list[float]


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[RagChunk] = []

    def add_document(self, doc_id: str, source: str, trust: str, content: str) -> None:
        for index, chunk in enumerate(chunk_text(content)):
            self._chunks.append(
                RagChunk(
                    doc_id=f"{doc_id}:{index}",
                    source=source,
                    trust=trust,
                    text=chunk,
                    embedding=embed_text(chunk),
                )
            )

    def add_many(self, docs: Iterable[tuple[str, str, str, str]]) -> None:
        for doc_id, source, trust, content in docs:
            self.add_document(doc_id, source, trust, content)

    def search(self, query: str, *, limit: int = 4) -> list[RagChunk]:
        query_embedding = embed_text(query)
        ranked = sorted(
            self._chunks,
            key=lambda chunk: cosine_similarity(query_embedding, chunk.embedding),
            reverse=True,
        )
        return ranked[:limit]
