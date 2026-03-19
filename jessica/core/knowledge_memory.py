import json
import os
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


class KnowledgeMemory:

    def __init__(self, path: str = "jessica/knowledge.json") -> None:

        self.path = path
        self.model: Any = SentenceTransformer("all-MiniLM-L6-v2")

        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load(self) -> list[dict[str, Any]]:

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: list[dict[str, Any]]) -> None:

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def remember(self, text: str) -> None:

        data = self.load()

        embedding_vec = np.asarray(
            self.model.encode(text, convert_to_numpy=True),
            dtype=float,
        )
        embedding = embedding_vec.tolist()

        data.append({
            "text": text,
            "embedding": embedding
        })

        self.save(data)

    def search(self, query: str, top_k: int = 3) -> list[str]:

        data = self.load()

        if not data:
            return []

        query_vec = np.asarray(
            self.model.encode(query, convert_to_numpy=True),
            dtype=float,
        )

        scored: list[tuple[float, str]] = []

        for item in data:

            emb = np.asarray(item["embedding"], dtype=float)

            score = float(np.dot(query_vec, emb) / (
                np.linalg.norm(query_vec) * np.linalg.norm(emb)
            ))

            scored.append((score, item["text"]))

        scored.sort(reverse=True)

        return [text for _, text in scored[:top_k]]
