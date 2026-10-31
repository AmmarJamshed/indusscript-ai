from analysis.frequency import frequency_report, js_divergence, sign_frequencies
from analysis.ngrams import extract_ngrams, ngram_report
from analysis.entropy import shannon_entropy, mutual_information
from analysis.positional import positional_probabilities


def sample_seqs():
    return [
        ["A", "B", "C"],
        ["A", "B", "D"],
        ["A", "E", "C"],
        ["B", "B", "C"],
    ]


def test_frequency_report():
    report = frequency_report(sample_seqs())
    assert report["inventory_size"] >= 4
    assert report["token_count"] == 12


def test_js_divergence_identical_zero():
    c = sign_frequencies(sample_seqs())
    assert js_divergence(c, c) == 0.0


def test_ngrams():
    bigrams = extract_ngrams(sample_seqs(), 2)
    assert ("A", "B") in bigrams
    report = ngram_report(sample_seqs())
    assert "2" in report["orders"]


def test_entropy_positive():
    assert shannon_entropy(sample_seqs()) > 0
    assert mutual_information(sample_seqs()) >= 0


def test_positional():
    probs = positional_probabilities(sample_seqs())
    assert "beginning" in probs
    assert abs(sum(probs["beginning"].values()) - 1.0) < 1e-6
