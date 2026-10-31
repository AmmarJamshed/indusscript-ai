"""Structural similarity across writing systems."""

from __future__ import annotations

from collections import Counter

import numpy as np

from analysis.entropy import entropy_report
from analysis.frequency import js_divergence, sign_frequencies
from analysis.ngrams import extract_ngrams
from analysis.positional import positional_probabilities


def length_distribution(sequences: list[list[str]]) -> dict:
    lengths = [len(s) for s in sequences]
    if not lengths:
        return {"mean": 0, "std": 0, "min": 0, "max": 0, "histogram": {}}
    hist = Counter(lengths)
    return {
        "mean": float(np.mean(lengths)),
        "std": float(np.std(lengths)),
        "min": int(min(lengths)),
        "max": int(max(lengths)),
        "histogram": {str(k): v for k, v in sorted(hist.items())},
    }


def repetition_rate(sequences: list[list[str]]) -> float:
    """Average fraction of tokens that repeat within an inscription."""
    rates = []
    for seq in sequences:
        if not seq:
            continue
        rates.append(1.0 - (len(set(seq)) / len(seq)))
    return float(np.mean(rates)) if rates else 0.0


def transition_matrix(sequences: list[list[str]], top_k: int = 20) -> dict:
    bigrams = extract_ngrams(sequences, 2)
    top_signs = [s for s, _ in sign_frequencies(sequences).most_common(top_k)]
    matrix = {a: {b: 0 for b in top_signs} for a in top_signs}
    for (a, b), c in bigrams.items():
        if a in matrix and b in matrix[a]:
            matrix[a][b] = c
    return matrix


def structural_report(sequences: list[list[str]], label: str) -> dict:
    return {
        "label": label,
        "research_question": "B",
        "length_distribution": length_distribution(sequences),
        "repetition_rate": repetition_rate(sequences),
        "positional": {
            k: dict(list(v.items())[:15])
            for k, v in positional_probabilities(sequences).items()
        },
        "entropy": entropy_report(sequences),
        "transition_top": [
            {"bigram": list(gram), "count": count}
            for gram, count in extract_ngrams(sequences, 2).most_common(20)
        ],
        "caveat": "Structural similarity ≠ linguistic relationship.",
    }


def compare_corpora(
    corpora: dict[str, list[list[str]]],
) -> dict:
    reports = {name: structural_report(seqs, name) for name, seqs in corpora.items()}
    js: dict[str, float] = {}
    names = list(corpora.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            key = f"{a}__vs__{b}"
            js[key] = js_divergence(
                sign_frequencies(corpora[a]), sign_frequencies(corpora[b])
            )
    return {
        "research_question": "B",
        "per_corpus": reports,
        "js_divergence": js,
        "integrity_note": (
            "JS divergence compares frequency structure only. It does not measure "
            "visual similarity (Q-A), contact (Q-C), or meaning (Q-D)."
        ),
    }
