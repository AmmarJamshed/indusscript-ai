"""Cross-checks for candidate hypotheses."""

from __future__ import annotations

from analysis.frequency import js_divergence, sign_frequencies
from analysis.ngrams import extract_ngrams
from hypotheses.candidate_languages import score_hypotheses


def out_of_sample_ngram_overlap(
    train: list[list[str]],
    test: list[list[str]],
    n: int = 2,
) -> dict:
    train_grams = set(extract_ngrams(train, n))
    test_grams = extract_ngrams(test, n)
    if not test_grams:
        return {"overlap_rate": 0.0, "n_test_grams": 0}
    hit = sum(c for g, c in test_grams.items() if g in train_grams)
    total = sum(test_grams.values())
    return {
        "overlap_rate": hit / total if total else 0.0,
        "n_test_grams": len(test_grams),
        "n_train_grams": len(train_grams),
        "caveat": "N-gram reuse is structural, not semantic validation.",
    }


def holdout_split(sequences: list[list[str]], ratio: float = 0.2, seed: int = 42):
    import random

    rng = random.Random(seed)
    seqs = list(sequences)
    rng.shuffle(seqs)
    cut = max(1, int(len(seqs) * ratio))
    return seqs[cut:], seqs[:cut]


def validate_hypothesis_bundle(indus_sequences: list[list[str]]) -> dict:
    train, test = holdout_split(indus_sequences)
    hyp_scores = [h.to_dict() for h in score_hypotheses()]
    return {
        "research_question": "D",
        "hypothesis_ranking": hyp_scores,
        "holdout_bigram_overlap": out_of_sample_ngram_overlap(train, test, 2),
        "note": (
            "Independent validation requires external bilinguals, reproducible "
            "phonetic assignments, or archaeological confirmations — none are "
            "claimed here."
        ),
    }
