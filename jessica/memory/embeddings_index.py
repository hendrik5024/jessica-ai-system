"""
EmbeddingsIndex: sentence-transformers + FAISS (if available) with persistence.
Features:
- build index from list of (id, text)
- add single embedding
- search by query text (returns list of ids, scores)
- persist index (vectors.npy + meta.json) and faiss index if used
"""

import os
import json
import numpy as np
from typing import List, Tuple, Optional

# Try to import faiss optionally
_FAISS_AVAILABLE = False
try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False

# sentence-transformers
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # small, good balance for local usage

class EmbeddingsIndex:
    def __init__(self, path: str = "jessica_data_embeddings"):
        """
        path: directory to store index and metadata
        """
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        self.model = SentenceTransformer(MODEL_NAME)
        self.id_to_meta = {}   # id -> meta dict (including original text)
        self.vectors = None    # np.ndarray shape (N, D)
        self.ids = []          # list of ids aligned with vectors rows
        self.faiss_index = None
        self.dim = self.model.get_sentence_embedding_dimension()
        # try load existing
        self._load()

    # ---------- Persistence ----------
    def _meta_path(self):
        return os.path.join(self.path, "meta.json")

    def _vectors_path(self):
        return os.path.join(self.path, "vectors.npy")

    def _ids_path(self):
        return os.path.join(self.path, "ids.json")

    def _faiss_path(self):
        return os.path.join(self.path, "faiss.index")

    def _load(self):
        # load meta & ids
        try:
            if os.path.exists(self._meta_path()):
                with open(self._meta_path(), "r", encoding="utf-8") as f:
                    self.id_to_meta = json.load(f)
            if os.path.exists(self._ids_path()):
                with open(self._ids_path(), "r", encoding="utf-8") as f:
                    self.ids = json.load(f)
            if os.path.exists(self._vectors_path()):
                self.vectors = np.load(self._vectors_path())
            # load faiss if available
            if _FAISS_AVAILABLE and os.path.exists(self._faiss_path()):
                try:
                    self.faiss_index = faiss.read_index(self._faiss_path())  # type: ignore
                except Exception as e:
                    print("[EmbIndex] failed loading faiss index:", e)
                    self.faiss_index = None
        except Exception as e:
            print("[EmbIndex] load error:", e)

    def _save(self):
        try:
            with open(self._meta_path(), "w", encoding="utf-8") as f:
                json.dump(self.id_to_meta, f, ensure_ascii=False, indent=2)
            with open(self._ids_path(), "w", encoding="utf-8") as f:
                json.dump(self.ids, f, default=str, indent=2)
            if self.vectors is not None:
                np.save(self._vectors_path(), self.vectors)
            if _FAISS_AVAILABLE and self.faiss_index is not None:
                try:
                    faiss.write_index(self.faiss_index, self._faiss_path())  # type: ignore
                except Exception as e:
                    print("[EmbIndex] failed writing faiss index:", e)
        except Exception as e:
            print("[EmbIndex] save error:", e)

    # ---------- Index building ----------
    def build_from_texts(self, items: List[Tuple[str, str, dict]]):
        """
        items: list of tuples (id, text, meta)
        meta is JSON-serializable (e.g. {"user":..., "ts":..., "type":...})
        This will overwrite the current index.
        """
        ids = []
        texts = []
        id_to_meta = {}
        for id_, text, meta in items:
            ids.append(str(id_))
            texts.append(text)
            id_to_meta[str(id_)] = meta or {}

        if not texts:
            # clear
            self.ids = []
            self.vectors = None
            self.id_to_meta = {}
            self.faiss_index = None
            self._save()
            return

        embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        # normalize embeddings for cosine similarity (faiss + numpy)
        embs = self._normalize(embs)

        self.ids = ids
        self.vectors = embs
        self.id_to_meta = id_to_meta

        if _FAISS_AVAILABLE:
            try:
                self.faiss_index = faiss.IndexFlatIP(self.dim)  # type: ignore
                self.faiss_index.add(embs.astype(np.float32))  # type: ignore
            except Exception as e:
                print("[EmbIndex] FAISS build error:", e)
                self.faiss_index = None

        self._save()

    def add(self, id_: str, text: str, meta: Optional[dict] = None):
        """
        Add a single item to the index (append).
        """
        id_s = str(id_)
        vec = self.model.encode([text], convert_to_numpy=True)
        vec = self._normalize(vec)[0]
        # append
        if self.vectors is None:
            self.vectors = np.array([vec])
            self.ids = [id_s]
        else:
            self.vectors = np.vstack([self.vectors, vec])
            self.ids.append(id_s)

        self.id_to_meta[id_s] = meta or {}
        # update faiss if available
        if _FAISS_AVAILABLE:
            try:
                if self.faiss_index is None:
                    self.faiss_index = faiss.IndexFlatIP(self.dim)  # type: ignore
                self.faiss_index.add(np.expand_dims(vec.astype(np.float32), axis=0))  # type: ignore
            except Exception as e:
                print("[EmbIndex] FAISS add error:", e)

        self._save()

    # ---------- Search ----------
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Returns list of (id, score) sorted by score desc.
        Score is cosine similarity between -1..1 (since vectors are normalized)
        """
        try:
            qv = self.model.encode([query], convert_to_numpy=True)
            qv = self._normalize(qv)[0]
        except Exception as e:
            print("[EmbIndex] encode error:", e)
            return []

        if self.vectors is None or len(self.ids) == 0:
            return []

        # FAISS path
        if _FAISS_AVAILABLE and self.faiss_index is not None:
            try:
                D, I = self.faiss_index.search(np.expand_dims(qv.astype(np.float32), axis=0), top_k)  # type: ignore
                results = []
                for score, idx in zip(D[0], I[0]):
                    if idx < 0 or idx >= len(self.ids):
                        continue
                    results.append((self.ids[int(idx)], float(score)))
                return results
            except Exception as e:
                print("[EmbIndex] faiss search error:", e)
                # fall through to numpy

        # numpy fallback: dot product because we normalized
        vecs = self.vectors
        scores = np.dot(vecs, qv)
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = [(self.ids[int(i)], float(scores[int(i)])) for i in top_idx]
        return results

    # ---------- Utilities ----------
    def _normalize(self, arr: np.ndarray) -> np.ndarray:
        # handle 2D arrays
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-10
        return arr / norms

    def get_meta(self, id_: str) -> dict:
        return self.id_to_meta.get(str(id_), {})

    def describe(self) -> dict:
        return {"count": len(self.ids), "faiss": _FAISS_AVAILABLE and self.faiss_index is not None}
"""
EmbeddingsIndex: sentence-transformers + FAISS (if available) with persistence.
Features:
- build index from list of (id, text)
- add single embedding
- search by query text (returns list of ids, scores)
- persist index (vectors.npy + meta.json) and faiss index if used
"""

import os
import json
import numpy as np
from typing import List, Tuple, Optional

_FAISS_AVAILABLE = False
try:
    import faiss  # type: ignore
    _FAISS_AVAILABLE = True
except Exception:
    _FAISS_AVAILABLE = False

from sentence_transformers import SentenceTransformer  # type: ignore

MODEL_NAME = "all-MiniLM-L6-v2"

class EmbeddingsIndex:
    def __init__(self, path: str = "jessica_data_embeddings"):
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        self.model = SentenceTransformer(MODEL_NAME)
        self.id_to_meta = {}
        self.vectors = None
        self.ids: List[str] = []
        self.faiss_index = None
        self.dim = self.model.get_sentence_embedding_dimension()
        self._load()

    def _meta_path(self):
        return os.path.join(self.path, "meta.json")

    def _vectors_path(self):
        return os.path.join(self.path, "vectors.npy")

    def _ids_path(self):
        return os.path.join(self.path, "ids.json")

    def _faiss_path(self):
        return os.path.join(self.path, "faiss.index")

    def _load(self):
        try:
            if os.path.exists(self._meta_path()):
                with open(self._meta_path(), "r", encoding="utf-8") as f:
                    self.id_to_meta = json.load(f)
            if os.path.exists(self._ids_path()):
                with open(self._ids_path(), "r", encoding="utf-8") as f:
                    self.ids = json.load(f)
            if os.path.exists(self._vectors_path()):
                self.vectors = np.load(self._vectors_path())
            if _FAISS_AVAILABLE and os.path.exists(self._faiss_path()):
                try:
                    self.faiss_index = faiss.read_index(self._faiss_path())
                except Exception as e:
                    print("[EmbIndex] failed loading faiss index:", e)
                    self.faiss_index = None
        except Exception as e:
            print("[EmbIndex] load error:", e)

    def _save(self):
        try:
            with open(self._meta_path(), "w", encoding="utf-8") as f:
                json.dump(self.id_to_meta, f, ensure_ascii=False, indent=2)
                with open(self._ids_path(), "w", encoding="utf-8") as f:
                    json.dump(self.ids, f, default=str, indent=2)
            if self.vectors is not None:
                np.save(self._vectors_path(), self.vectors)
            if _FAISS_AVAILABLE and self.faiss_index is not None:
                try:
                    faiss.write_index(self.faiss_index, self._faiss_path())
                except Exception as e:
                    print("[EmbIndex] failed writing faiss index:", e)
        except Exception as e:
            print("[EmbIndex] save error:", e)

    def build_from_texts(self, items: List[Tuple[str, str, dict]]):
        ids: List[str] = []
        texts: List[str] = []
        id_to_meta = {}
        for id_, text, meta in items:
            ids.append(str(id_))
            texts.append(text)
            id_to_meta[str(id_)] = meta or {}

        if not texts:
            self.ids = []
            self.vectors = None
            self.id_to_meta = {}
            self.faiss_index = None
            self._save()
            return

        embs = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        embs = self._normalize(embs)

        self.ids = ids
        self.vectors = embs
        self.id_to_meta = id_to_meta

        if _FAISS_AVAILABLE:
            try:
                self.faiss_index = faiss.IndexFlatIP(self.dim)
                self.faiss_index.add(embs)
            except Exception as e:
                print("[EmbIndex] FAISS build error:", e)
                self.faiss_index = None

        self._save()

    def add(self, id_: str, text: str, meta: Optional[dict] = None):
        id_s = str(id_)
        vec = self.model.encode([text], convert_to_numpy=True)
        vec = self._normalize(vec)[0]
        if self.vectors is None:
            self.vectors = np.array([vec])
            self.ids = [id_s]
        else:
            self.vectors = np.vstack([self.vectors, vec])
            self.ids.append(id_s)

        self.id_to_meta[id_s] = meta or {}
        if _FAISS_AVAILABLE:
            try:
                if self.faiss_index is None:
                    self.faiss_index = faiss.IndexFlatIP(self.dim)
                self.faiss_index.add(np.expand_dims(vec, axis=0))
            except Exception as e:
                print("[EmbIndex] FAISS add error:", e)

        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        try:
            qv = self.model.encode([query], convert_to_numpy=True)
            qv = self._normalize(qv)[0]
        except Exception as e:
            print("[EmbIndex] encode error:", e)
            return []

        if self.vectors is None or len(self.ids) == 0:
            return []

        if _FAISS_AVAILABLE and self.faiss_index is not None:
            try:
                D, I = self.faiss_index.search(np.expand_dims(qv, axis=0).astype(np.float32), top_k)
                results = []
                for score, idx in zip(D[0], I[0]):
                    if idx < 0 or idx >= len(self.ids):
                        continue
                    results.append((self.ids[int(idx)], float(score)))
                return results
            except Exception as e:
                print("[EmbIndex] faiss search error:", e)

        scores = np.dot(self.vectors, qv)
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = [(self.ids[int(i)], float(scores[int(i)])) for i in top_idx]
        return results

    def _normalize(self, arr: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-10
        return arr / norms

    def get_meta(self, id_: str) -> dict:
        return self.id_to_meta.get(str(id_), {})

    def describe(self) -> dict:
        return {"count": len(self.ids), "faiss": _FAISS_AVAILABLE and self.faiss_index is not None}
