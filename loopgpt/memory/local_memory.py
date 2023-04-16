from loopgpt.memory.base_memory import BaseMemory
import numpy as np
from typing import *


class LocalMemory(BaseMemory):
    def __init__(self, embedding_provider: callable):
        super(BaseMemory, self).__init__()
        self.docs: List[str] = []
        self.embs: Optional[np.ndarray] = None
        self.embedding_provider = embedding_provider

    def add(self, doc: str):
        emb = self.embedding_provider(doc)
        if self.embs is None:
            self.embs = np.expand_dims(emb, 0)
        else:
            self.embs = np.concatenate([self.embs, [emb]], 0)
        self.docs.append(doc)

    def get(self, query: str, k: int):
        if self.embs is None:
            return []
        emb = self.embedding_provider(query)
        scores = self.embs.dot(emb)
        idxs = np.argsort(scores)[-k:][::-1]
        return [self.docs[i] for i in idxs]

    def _serialize_embs(self):
        if self.embs is None:
            return None
        return {
            "dtype": self.embs.dtype.name,
            "data": self.embs.tolist(),
            "shape": self.embs.shape,
        }

    def config(self):
        cfg = super().config()
        cfg.update(
            {
                "docs": self.docs,
                "embs": self._serialize_embs(),
                "embedding_provider": self.embedding_provider.serialize(),
            }
        )

    @classmethod
    def from_config(cls, config):
        obj = cls()
        obj.docs = config["docs"]
        embs = config["embs"]
        if embs is not None:
            obj.embs = np.array(embs["data"], dtype=embs["dtype"]).reshape(
                embs["shape"]
            )
        return obj
