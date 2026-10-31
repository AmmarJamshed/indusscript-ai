"""Hypothesis generation, validation and falsification."""

from hypotheses.candidate_languages import score_hypotheses
from hypotheses.inference import generate_candidates, interpretation_report
from hypotheses.falsification import run_falsification_suite
from hypotheses.speculative_translator import english_to_indus, indus_to_english_hypothesis

__all__ = [
    "english_to_indus",
    "generate_candidates",
    "indus_to_english_hypothesis",
    "interpretation_report",
    "run_falsification_suite",
    "score_hypotheses",
]
