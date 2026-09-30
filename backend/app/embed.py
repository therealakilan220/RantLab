"""Text embeddings (Member 2). Real mode: MiniLM. Stub mode: a cheap word-hash vector."""
import hashlib
import re

import numpy as np

from . import config

_STOP = {"the", "and", "for", "that", "this", "with", "are", "was", "has", "have", "but", "not", "you", "our", "its"}
_model = None


def _hash_embed(text: str, dim: int = 128) -> list[float]:
    vec = np.zeros(dim)
    for word in re.findall(r"[a-z]+", text.lower()):
        if len(word) > 2 and word not in _STOP:
            vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % dim] += 1
    return vec.tolist()


def embed(text: str) -> list[float]:
    if config.STUB_MODE:
        return _hash_embed(text)
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # heavy import, load once

        _model = SentenceTransformer(config.EMBED_MODEL)
    return _model.encode(text, normalize_embeddings=True).tolist()


def warm_up() -> None:
    if not config.STUB_MODE:
        embed("warm up")
