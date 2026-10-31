"""Sign frequency distributions and Jensen-Shannon divergence."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np
from scipy.spatial.distance import jensenshannon


def sign_frequencies(sequences: Iterable[list[str]]) -> Counter:
    counts: Counter = Counter()
    for seq in sequences:
        counts.update(seq)
    return counts


def relative_frequencies(counts: Counter) -> dict[str, float]:
    total = sum(counts.values()) or 1
    return {k: v / total for k, v in counts.items()}


def rank_frequency(counts: Counter) -> list[tuple[str, int, int]]:
    """Return (sign, count, rank) sorted by descending frequency."""
    ranked = counts.most_common()
    return [(sign, count, rank + 1) for rank, (sign, count) in enumerate(ranked)]


def rare_signs(counts: Counter, max_count: int = 1) -> list[str]:
    return [s for s, c in counts.items() if c <= max_count]


def frequencies_by_site(
    records: list,  # HistoricalRecord-like with archaeological_site + sign_sequence
) -> dict[str, Counter]:
    by_site: dict[str, Counter] = {}
    for rec in records:
        site = getattr(rec, "archaeological_site", None) or "UNKNOWN"
        by_site.setdefault(site, Counter()).update(getattr(rec, "sign_sequence", []) or [])
    return by_site


def js_divergence(
    counts_a: Counter,
    counts_b: Counter,
    base: float = 2.0,
) -> float:
    """Jensen-Shannon divergence between two sign distributions."""
    vocab = sorted(set(counts_a) | set(counts_b))
    if not vocab:
        return 0.0
    a = np.array([counts_a.get(s, 0) for s in vocab], dtype=float)
    b = np.array([counts_b.get(s, 0) for s in vocab], dtype=float)
    a = a / (a.sum() or 1.0)
    b = b / (b.sum() or 1.0)
    return float(jensenshannon(a, b, base=base) ** 2)


def frequency_report(sequences: list[list[str]]) -> dict:
    counts = sign_frequencies(sequences)
    rel = relative_frequencies(counts)
    ranked = rank_frequency(counts)
    return {
        "research_question": "B",
        "n_sequences": len(sequences),
        "inventory_size": len(counts),
        "token_count": int(sum(counts.values())),
        "top_20": ranked[:20],
        "rare_signs": rare_signs(counts),
        "relative_frequencies": dict(sorted(rel.items(), key=lambda x: -x[1])[:50]),
        "caveat": "Frequency similarity is not evidence of shared meaning or ancestry.",
    }
