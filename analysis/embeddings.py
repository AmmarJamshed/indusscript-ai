"""Contextual embeddings for sign sequences.

Embedding similarity is a computational observation — never semantic proof.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from config.logging_config import setup_logging

logger = setup_logging("analysis.embeddings")


def _corpus_as_sentences(sequences: list[list[str]]) -> list[list[str]]:
    return [list(seq) for seq in sequences if seq]


def train_word2vec(
    sequences: list[list[str]],
    vector_size: int = 32,
    window: int = 2,
    min_count: int = 1,
    epochs: int = 50,
) -> Any | None:
    try:
        from gensim.models import Word2Vec
    except ImportError:
        logger.warning("gensim not installed; skipping Word2Vec")
        return None
    sentences = _corpus_as_sentences(sequences)
    if not sentences:
        return None
    model = Word2Vec(
        sentences=sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=1,
        sg=1,
        epochs=epochs,
        seed=42,
    )
    return model


def train_fasttext(
    sequences: list[list[str]],
    vector_size: int = 32,
    window: int = 2,
    min_count: int = 1,
    epochs: int = 50,
) -> Any | None:
    try:
        from gensim.models import FastText
    except ImportError:
        logger.warning("gensim not installed; skipping FastText")
        return None
    sentences = _corpus_as_sentences(sequences)
    if not sentences:
        return None
    model = FastText(
        sentences=sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=1,
        epochs=epochs,
        seed=42,
    )
    return model


def token_vectors(model: Any) -> dict[str, list[float]]:
    if model is None:
        return {}
    keyed = model.wv
    return {tok: keyed[tok].tolist() for tok in keyed.index_to_key}


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def align_by_frequency_anchor(
    vectors_a: dict[str, list[float]],
    vectors_b: dict[str, list[float]],
    anchors_a: list[str],
    anchors_b: list[str],
) -> dict:
    """Documented naive alignment via paired frequency anchors.

    Requires equal-length explicit anchor lists chosen by the analyst.
    Does NOT assume semantic equivalence.
    """
    if len(anchors_a) != len(anchors_b) or not anchors_a:
        return {
            "error": "Anchor lists must be non-empty and equal length",
            "caveat": "Alignment is analyst-supervised, not automatic decipherment.",
        }
    mats_a = []
    mats_b = []
    used = []
    for xa, xb in zip(anchors_a, anchors_b):
        if xa in vectors_a and xb in vectors_b:
            mats_a.append(vectors_a[xa])
            mats_b.append(vectors_b[xb])
            used.append((xa, xb))
    if len(used) < 2:
        return {"error": "Need at least 2 valid anchors", "used": used}
    A = np.array(mats_a)
    B = np.array(mats_b)
    # Orthogonal Procrustes
    M = B.T @ A
    U, _, Vt = np.linalg.svd(M)
    R = U @ Vt
    transformed = {k: (R @ np.array(v)).tolist() for k, v in vectors_a.items()}
    return {
        "research_question": "B",
        "method": "orthogonal_procrustes_frequency_anchors",
        "anchors_used": used,
        "rotation_shape": list(R.shape),
        "transformed_a_sample": dict(list(transformed.items())[:10]),
        "caveat": (
            "Embedding alignment measures geometric correspondence under chosen anchors. "
            "It is not evidence of shared meaning (Q-D) or genetic relationship (Q-C)."
        ),
    }


def masked_sign_baseline(
    sequences: list[list[str]], mask_rate: float = 0.15
) -> dict:
    """Simple frequency-based masked prediction baseline (no Transformer required).

    A full Transformer masked-sign model can be plugged in when torch/transformers
    are installed; this baseline documents the evaluation protocol.
    """
    rng = np.random.default_rng(42)
    counts = Counter(t for s in sequences for t in s)
    if not counts:
        return {"accuracy": 0.0, "n": 0}
    most_common = counts.most_common(1)[0][0]
    total = 0
    correct = 0
    for seq in sequences:
        if len(seq) < 2:
            continue
        for i, tok in enumerate(seq):
            if rng.random() > mask_rate:
                continue
            total += 1
            # Predict most frequent sign (naive baseline)
            if most_common == tok:
                correct += 1
    return {
        "research_question": "B",
        "method": "frequency_baseline_masked_prediction",
        "accuracy": (correct / total) if total else 0.0,
        "n_masked": total,
        "note": "Replace with Transformer MLM when GPU stack is available.",
        "caveat": "Predictability ≠ decipherment.",
    }


def embedding_report(sequences: list[list[str]], label: str) -> dict:
    w2v = train_word2vec(sequences)
    ft = train_fasttext(sequences)
    w2v_vecs = token_vectors(w2v)
    ft_vecs = token_vectors(ft)
    backend = "gensim"
    if not w2v_vecs:
        from analysis.embeddings_numpy import train_cooccurrence_vectors

        w2v_vecs = train_cooccurrence_vectors(sequences)
        backend = "numpy_cooccurrence_svd_fallback"
    return {
        "label": label,
        "research_question": "B",
        "backend": backend,
        "word2vec_vocab": len(w2v_vecs),
        "fasttext_vocab": len(ft_vecs),
        "word2vec_vectors_sample": dict(list(w2v_vecs.items())[:5]),
        "masked_baseline": masked_sign_baseline(sequences),
        "caveat": "Do not interpret embedding proximity as semantic equivalence.",
    }
