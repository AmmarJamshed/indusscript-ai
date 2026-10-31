"""Positional sign probabilities: beginning / middle / ending."""

from __future__ import annotations

from collections import Counter
from typing import Literal

Position = Literal["beginning", "middle", "ending"]


def positional_counts(sequences: list[list[str]]) -> dict[Position, Counter]:
    beginning: Counter = Counter()
    middle: Counter = Counter()
    ending: Counter = Counter()
    for seq in sequences:
        if not seq:
            continue
        if len(seq) == 1:
            beginning[seq[0]] += 1
            ending[seq[0]] += 1
            continue
        beginning[seq[0]] += 1
        ending[seq[-1]] += 1
        for s in seq[1:-1]:
            middle[s] += 1
    return {"beginning": beginning, "middle": middle, "ending": ending}


def positional_probabilities(sequences: list[list[str]]) -> dict[str, dict[str, float]]:
    counts = positional_counts(sequences)
    out: dict[str, dict[str, float]] = {}
    for pos, ctr in counts.items():
        total = sum(ctr.values()) or 1
        out[pos] = {s: c / total for s, c in ctr.most_common()}
    return out


def boundary_enriched_signs(
    sequences: list[list[str]], min_count: int = 3
) -> list[dict]:
    """Signs that appear disproportionately at boundaries vs middle."""
    counts = positional_counts(sequences)
    all_signs = set(counts["beginning"]) | set(counts["middle"]) | set(counts["ending"])
    results = []
    for sign in all_signs:
        b = counts["beginning"][sign]
        m = counts["middle"][sign]
        e = counts["ending"][sign]
        total = b + m + e
        if total < min_count:
            continue
        boundary = b + e
        boundary_share = boundary / total
        mid_share = m / total
        results.append(
            {
                "sign": sign,
                "beginning": b,
                "middle": m,
                "ending": e,
                "boundary_share": boundary_share,
                "middle_share": mid_share,
            }
        )
    results.sort(key=lambda x: -x["boundary_share"])
    return results


def compare_directions(sequences: list[list[str]]) -> dict:
    """Compare positional stats for original vs reversed reading."""
    reversed_seqs = [list(reversed(s)) for s in sequences]
    return {
        "research_question": "B",
        "original": positional_probabilities(sequences),
        "reversed": positional_probabilities(reversed_seqs),
        "boundary_enriched_original": boundary_enriched_signs(sequences)[:20],
        "boundary_enriched_reversed": boundary_enriched_signs(reversed_seqs)[:20],
        "note": "When direction is UNKNOWN, report both orientations without choosing one.",
    }
