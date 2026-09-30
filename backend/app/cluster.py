"""Group similar complaints (Member 2).

Simple version: link any two complaints whose cosine similarity is >= threshold,
then take connected groups. Easy to explain and fast. If it chains unrelated
complaints together, raise the threshold or switch to agglomerative clustering.
"""
from collections import Counter

import numpy as np


def _matrix(items: list[tuple[str, list[float]]]):
    """Keep only embeddings of the most common length, so old stub and real vectors can't mix."""
    if not items:
        return [], np.zeros((0, 0))
    dim = Counter(len(e) for _, e in items).most_common(1)[0][0]
    kept = [(i, e) for i, e in items if len(e) == dim]
    mat = np.array([e for _, e in kept], dtype=float)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return [i for i, _ in kept], mat / norms


def cluster(items: list[tuple[str, list[float]]], threshold: float = 0.6) -> dict[str, str]:
    """items = (card_id, embedding). Returns {card_id: cluster_id}."""
    ids, mat = _matrix(items)
    if not ids:
        return {}
    sim = mat @ mat.T
    parent = list(range(len(ids)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if sim[i, j] >= threshold:
                parent[find(i)] = find(j)

    groups: dict[int, list[str]] = {}
    for idx, card_id in enumerate(ids):
        groups.setdefault(find(idx), []).append(card_id)

    out: dict[str, str] = {}
    for members in groups.values():
        cluster_id = "k_" + min(members).removeprefix("c_")
        for m in members:
            out[m] = cluster_id
    return out


def most_central(items: list[tuple[str, list[float]]], members: list[str]) -> str:
    """The member most similar to the rest. Its text makes a good cluster label."""
    if len(members) == 1:
        return members[0]
    ids, mat = _matrix([(i, e) for i, e in items if i in set(members)])
    if not ids:
        return members[0]
    sim = mat @ mat.T
    return ids[int(sim.mean(axis=1).argmax())]
