"""N-gram analysis for sign sequences."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable


def extract_ngrams(sequences: Iterable[list[str]], n: int) -> Counter:
    counts: Counter = Counter()
    for seq in sequences:
        if len(seq) < n:
            continue
        for i in range(len(seq) - n + 1):
            gram = tuple(seq[i : i + n])
            counts[gram] += 1
    return counts


def conditional_probabilities(sequences: list[list[str]], n: int = 2) -> dict:
    """P(next | context) for n-grams where context length is n-1."""
    if n < 2:
        raise ValueError("n must be >= 2 for conditional probabilities")
    joint = extract_ngrams(sequences, n)
    context_counts: Counter = Counter()
    for gram, c in joint.items():
        context_counts[gram[:-1]] += c
    probs: dict[str, dict[str, float]] = defaultdict(dict)
    for gram, c in joint.items():
        ctx = gram[:-1]
        nxt = gram[-1]
        probs["|".join(ctx)][nxt] = c / context_counts[ctx]
    return dict(probs)


def repeated_sequences(
    sequences: list[list[str]], min_n: int = 2, max_n: int = 4, min_count: int = 2
) -> list[dict]:
    out: list[dict] = []
    for n in range(min_n, max_n + 1):
        counts = extract_ngrams(sequences, n)
        for gram, c in counts.most_common():
            if c < min_count:
                break
            out.append({"n": n, "sequence": list(gram), "count": c})
    return out


def ngram_report(sequences: list[list[str]], orders: tuple[int, ...] = (1, 2, 3, 4)) -> dict:
    by_order = {}
    for n in orders:
        counts = extract_ngrams(sequences, n)
        top = [{"sequence": list(g), "count": c} for g, c in counts.most_common(30)]
        by_order[str(n)] = {"unique": len(counts), "top": top}
    return {
        "research_question": "B",
        "orders": by_order,
        "repeated": repeated_sequences(sequences),
        "conditional_bigrams_sample": dict(
            list(conditional_probabilities(sequences, 2).items())[:40]
        ),
        "caveat": "Recurring n-grams may reflect administrative formulae, not language.",
    }
