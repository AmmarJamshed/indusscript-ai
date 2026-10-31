"""NumPy fallback skip-gram-style co-occurrence embeddings (no gensim required)."""

from __future__ import annotations

from collections import Counter

import numpy as np


def train_cooccurrence_vectors(
    sequences: list[list[str]],
    vector_size: int = 32,
    window: int = 2,
    seed: int = 42,
) -> dict[str, list[float]]:
    vocab = sorted({t for s in sequences for t in s})
    if not vocab:
        return {}
    index = {t: i for i, t in enumerate(vocab)}
    mat = np.zeros((len(vocab), len(vocab)), dtype=np.float64)
    for seq in sequences:
        for i, tok in enumerate(seq):
            for j in range(max(0, i - window), min(len(seq), i + window + 1)):
                if i == j:
                    continue
                mat[index[tok], index[seq[j]]] += 1.0
    # SVD of PPMI-ish matrix
    row_sum = mat.sum(axis=1, keepdims=True) + 1e-9
    col_sum = mat.sum(axis=0, keepdims=True) + 1e-9
    total = mat.sum() + 1e-9
    pmi = np.log((mat * total) / (row_sum @ col_sum) + 1e-9)
    pmi = np.maximum(pmi, 0)
    k = min(vector_size, min(pmi.shape))
    try:
        u, s, _ = np.linalg.svd(pmi, full_matrices=False)
        vecs = u[:, :k] * np.sqrt(s[:k])
    except np.linalg.LinAlgError:
        rng = np.random.default_rng(seed)
        vecs = rng.normal(size=(len(vocab), k))
    if vecs.shape[1] < vector_size:
        pad = np.zeros((len(vocab), vector_size - vecs.shape[1]))
        vecs = np.hstack([vecs, pad])
    return {tok: vecs[index[tok]].tolist() for tok in vocab}
