from hypotheses.falsification import (
    benjamini_hochberg,
    bootstrap_ci,
    frequency_preserving_shuffle,
    run_falsification_suite,
)
import numpy as np


def test_shuffle_preserves_multiset():
    seqs = [["A", "B", "A"], ["C", "A"]]
    rng = np.random.default_rng(0)
    shuf = frequency_preserving_shuffle(seqs, rng)
    assert sorted(t for s in seqs for t in s) == sorted(t for s in shuf for t in s)
    assert [len(s) for s in seqs] == [len(s) for s in shuf]


def test_bh():
    flags = benjamini_hochberg([0.001, 0.02, 0.5], q=0.05)
    assert flags[0] is True


def test_bootstrap_ci():
    ci = bootstrap_ci([1.0, 1.1, 0.9, 1.05], n_boot=100)
    assert ci["ci_low"] <= ci["mean"] <= ci["ci_high"]


def test_falsification_runs():
    indus = [["A", "B", "C"], ["A", "B", "D"], ["A", "E", "C"]] * 5
    other = [["X", "Y", "Z"], ["X", "Y", "W"], ["Q", "Y", "Z"]] * 5
    result = run_falsification_suite(indus, other, n_perm=50)
    assert "tests" in result
    assert result["n_permutations"] == 50
