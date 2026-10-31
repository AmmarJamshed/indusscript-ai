"""Comparative statistical analysis package."""

from analysis.frequency import frequency_report, js_divergence
from analysis.ngrams import ngram_report
from analysis.entropy import entropy_report
from analysis.positional import compare_directions, positional_probabilities
from analysis.sequence_analysis import compare_corpora, structural_report
from analysis.embeddings import embedding_report

__all__ = [
    "compare_corpora",
    "compare_directions",
    "embedding_report",
    "entropy_report",
    "frequency_report",
    "js_divergence",
    "ngram_report",
    "positional_probabilities",
    "structural_report",
]
