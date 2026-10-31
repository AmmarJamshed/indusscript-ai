"""Statistical falsification engine.

A hypothesis is penalised if apparent similarity is reproducible by random
or frequency-preserving null models.
"""

from __future__ import annotations

from collections import Counter
from typing import Callable

import numpy as np
from scipy import stats

from analysis.frequency import js_divergence, sign_frequencies
from analysis.entropy import shannon_entropy, mutual_information
from config.settings import DEFAULT_BOOTSTRAP_SAMPLES, DEFAULT_FALSIFICATION_PERMUTATIONS


def frequency_preserving_shuffle(
    sequences: list[list[str]], rng: np.random.Generator
) -> list[list[str]]:
    tokens = [t for s in sequences for t in s]
    rng.shuffle(tokens)
    out: list[list[str]] = []
    idx = 0
    for s in sequences:
        n = len(s)
        out.append(tokens[idx : idx + n])
        idx += n
    return out


def random_sequences_matched(
    sequences: list[list[str]], inventory: list[str], rng: np.random.Generator
) -> list[list[str]]:
    return [
        [inventory[i] for i in rng.integers(0, len(inventory), size=len(s))]
        for s in sequences
    ]


def length_matched_control(
    sequences: list[list[str]], donor: list[list[str]], rng: np.random.Generator
) -> list[list[str]]:
    """Build control corpus with Indus lengths but donor-token draws."""
    donor_tokens = [t for s in donor for t in s]
    if not donor_tokens:
        return sequences
    return [
        [donor_tokens[i] for i in rng.integers(0, len(donor_tokens), size=len(s))]
        for s in sequences
    ]


def permutation_test(
    observed: float,
    null_values: list[float],
    alternative: str = "greater",
) -> dict:
    null = np.asarray(null_values, dtype=float)
    if alternative == "greater":
        p = float(np.mean(null >= observed))
    elif alternative == "less":
        p = float(np.mean(null <= observed))
    else:
        p = float(np.mean(np.abs(null) >= abs(observed)))
    return {
        "observed": observed,
        "null_mean": float(null.mean()) if len(null) else 0.0,
        "null_std": float(null.std()) if len(null) else 0.0,
        "p_value": p,
        "n_permutations": len(null),
    }


def bootstrap_ci(
    values: list[float],
    n_boot: int = DEFAULT_BOOTSTRAP_SAMPLES,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0}
    boots = [
        float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
        for _ in range(n_boot)
    ]
    low, high = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return {
        "mean": float(arr.mean()),
        "ci_low": float(low),
        "ci_high": float(high),
        "n_boot": n_boot,
    }


def benjamini_hochberg(p_values: list[float], q: float = 0.05) -> list[bool]:
    """Multiple hypothesis correction (BH FDR)."""
    m = len(p_values)
    if m == 0:
        return []
    order = np.argsort(p_values)
    ranked = np.asarray(p_values)[order]
    thresh = q * (np.arange(1, m + 1) / m)
    below = ranked <= thresh
    if not np.any(below):
        return [False] * m
    max_k = np.max(np.where(below)[0])
    significant = np.zeros(m, dtype=bool)
    significant[order[: max_k + 1]] = True
    return significant.tolist()


def run_falsification_suite(
    indus: list[list[str]],
    comparison: list[list[str]],
    n_perm: int = DEFAULT_FALSIFICATION_PERMUTATIONS,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    observed_js = js_divergence(sign_frequencies(indus), sign_frequencies(comparison))
    observed_mi = mutual_information(indus)
    observed_h = shannon_entropy(indus)

    inventory = list(sign_frequencies(indus).keys()) or ["X"]
    null_js_shuffle = []
    null_js_random = []
    null_js_donor = []
    null_mi = []

    # Cap permutations for responsiveness; caller can raise n_perm.
    n_perm = max(50, min(n_perm, 5000))
    for _ in range(n_perm):
        shuf = frequency_preserving_shuffle(indus, rng)
        rnd = random_sequences_matched(indus, inventory, rng)
        donor = length_matched_control(indus, comparison, rng)
        null_js_shuffle.append(
            js_divergence(sign_frequencies(shuf), sign_frequencies(comparison))
        )
        null_js_random.append(
            js_divergence(sign_frequencies(rnd), sign_frequencies(comparison))
        )
        null_js_donor.append(
            js_divergence(sign_frequencies(donor), sign_frequencies(comparison))
        )
        null_mi.append(mutual_information(shuf))

    tests = {
        "js_vs_comparison_shuffle_null": permutation_test(
            observed_js, null_js_shuffle, alternative="less"
        ),
        "js_vs_comparison_random_null": permutation_test(
            observed_js, null_js_random, alternative="less"
        ),
        "js_vs_length_matched_donor": permutation_test(
            observed_js, null_js_donor, alternative="less"
        ),
        "mutual_information_vs_shuffle": permutation_test(
            observed_mi, null_mi, alternative="greater"
        ),
    }

    pvals = [t["p_value"] for t in tests.values()]
    rejected = benjamini_hochberg(pvals, q=0.05)

    # Negative control: compare two random corpora
    inv_c = list(sign_frequencies(comparison).keys()) or inventory
    neg_a = random_sequences_matched(indus, inventory, rng)
    neg_b = random_sequences_matched(comparison, inv_c, rng)
    negative_js = js_divergence(sign_frequencies(neg_a), sign_frequencies(neg_b))

    return {
        "research_question": "B/C/D falsification",
        "n_permutations": n_perm,
        "observed": {
            "js_divergence_indus_vs_comparison": observed_js,
            "indus_mutual_information": observed_mi,
            "indus_shannon_entropy": observed_h,
            "negative_control_js": negative_js,
        },
        "tests": tests,
        "bh_significant": {
            name: bool(flag) for name, flag in zip(tests.keys(), rejected)
        },
        "bootstrap_mi": bootstrap_ci(null_mi),
        "interpretation_guide": {
            "penalty_rule": (
                "Penalise a similarity hypothesis if observed JS or MI is not "
                "distinguishable from frequency-preserving or random controls."
            ),
            "caveat": (
                "Failure to reject a null does not prove unrelatedness; "
                "rejection does not prove decipherment or shared ancestry."
            ),
        },
    }


def cross_validate_js(
    sequences_a: list[list[str]],
    sequences_b: list[list[str]],
    folds: int = 5,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    idx = np.arange(len(sequences_a))
    rng.shuffle(idx)
    folds = min(folds, max(2, len(sequences_a)))
    chunks = np.array_split(idx, folds)
    scores = []
    for k in range(folds):
        test_idx = set(chunks[k].tolist())
        train = [sequences_a[i] for i in range(len(sequences_a)) if i not in test_idx]
        scores.append(
            js_divergence(sign_frequencies(train), sign_frequencies(sequences_b))
        )
    return {"fold_js": scores, "mean_js": float(np.mean(scores)) if scores else 0.0}
