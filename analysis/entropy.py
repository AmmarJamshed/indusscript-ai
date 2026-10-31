"""Information-theoretic measures for sign sequences."""

from __future__ import annotations

from collections import Counter
from math import log2

import numpy as np

from analysis.frequency import relative_frequencies, sign_frequencies
from analysis.ngrams import extract_ngrams


def shannon_entropy(sequences: list[list[str]]) -> float:
    rel = relative_frequencies(sign_frequencies(sequences))
    return float(-sum(p * log2(p) for p in rel.values() if p > 0))


def conditional_entropy(sequences: list[list[str]]) -> float:
    """H(X_{t+1} | X_t) from bigrams."""
    bigrams = extract_ngrams(sequences, 2)
    if not bigrams:
        return 0.0
    uni = sign_frequencies(sequences)
    # H(Y|X) = - sum p(x,y) log p(y|x)
    total = sum(bigrams.values()) or 1
    h = 0.0
    context_totals: Counter = Counter()
    for (a, b), c in bigrams.items():
        context_totals[a] += c
    for (a, b), c in bigrams.items():
        p_xy = c / total
        p_y_given_x = c / context_totals[a]
        h -= p_xy * log2(p_y_given_x)
    return float(h)


def mutual_information(sequences: list[list[str]]) -> float:
    """I(X_t; X_{t+1}) = H(X) - H(X_{t+1}|X_t) using unigram H as approximation."""
    h = shannon_entropy(sequences)
    return float(h - conditional_entropy(sequences))


def sequence_complexity(seq: list[str]) -> float:
    """Normalised unique-sign ratio as a simple complexity proxy."""
    if not seq:
        return 0.0
    return len(set(seq)) / len(seq)


def mean_sequence_complexity(sequences: list[list[str]]) -> float:
    if not sequences:
        return 0.0
    return float(np.mean([sequence_complexity(s) for s in sequences]))


def sign_predictability(sequences: list[list[str]]) -> float:
    """1 - H_cond / log2(|V|) clipped — higher means more predictable."""
    vocab = len(sign_frequencies(sequences))
    if vocab <= 1:
        return 1.0
    h_cond = conditional_entropy(sequences)
    max_h = log2(vocab)
    return float(max(0.0, min(1.0, 1.0 - (h_cond / max_h))))


def entropy_report(sequences: list[list[str]]) -> dict:
    lengths = [len(s) for s in sequences]
    return {
        "research_question": "B",
        "shannon_entropy": shannon_entropy(sequences),
        "conditional_entropy": conditional_entropy(sequences),
        "mutual_information": mutual_information(sequences),
        "mean_sequence_complexity": mean_sequence_complexity(sequences),
        "sign_predictability": sign_predictability(sequences),
        "n_sequences": len(sequences),
        "mean_length": float(np.mean(lengths)) if lengths else 0.0,
        "inventory_size": len(sign_frequencies(sequences)),
        "caveat": (
            "Entropy comparisons must account for text length, genre and inventory size. "
            "Similar entropy does not imply related languages."
        ),
    }
