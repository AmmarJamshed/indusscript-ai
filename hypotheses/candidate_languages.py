"""Candidate language hypotheses for the Indus writing system.

Scores are heuristic research aids — not conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass

from database.models import EvidenceTier, HypothesisScore


@dataclass
class LanguageHypothesis:
    hypothesis_id: str
    label: str
    family: str
    description: str
    chronological_window: str
    geographic_window: str


CANDIDATE_HYPOTHESES: list[LanguageHypothesis] = [
    LanguageHypothesis(
        "h_proto_dravidian",
        "Proto-Dravidian",
        "Dravidian",
        "Hypothesis that Indus inscriptions encode an early Dravidian language.",
        "approx. 3rd–2nd millennium BCE (debated)",
        "Northwest South Asia / Indus region (debated)",
    ),
    LanguageHypothesis(
        "h_early_dravidian",
        "Early Dravidian",
        "Dravidian",
        "A later or regionally differentiated Dravidian variety.",
        "2nd millennium BCE (debated)",
        "Indus / adjacent regions (debated)",
    ),
    LanguageHypothesis(
        "h_munda",
        "Munda-related",
        "Austroasiatic",
        "Hypothesis linking Indus language to Munda / Austroasiatic.",
        "debated",
        "South Asia (debated)",
    ),
    LanguageHypothesis(
        "h_indo_aryan",
        "Indo-Aryan-related",
        "Indo-European",
        "Hypothesis of early Indo-Aryan linguistic content (chronologically contested).",
        "often argued as too late for Mature Harappan by many specialists",
        "Northwest South Asia (debated)",
    ),
    LanguageHypothesis(
        "h_other",
        "Other language families",
        "Other",
        "Placeholder for Burushaski, isolate relatives, or undocumented families.",
        "unknown",
        "unknown",
    ),
    LanguageHypothesis(
        "h_isolate",
        "Language isolate",
        "Isolate",
        "Indus language unrelated to surviving families.",
        "3rd millennium BCE",
        "Indus Valley",
    ),
    LanguageHypothesis(
        "h_nonlinguistic",
        "Non-linguistic / predominantly administrative symbol system",
        "Non-linguistic",
        "Signs primarily non-linguistic (heraldic, accounting, etc.).",
        "Mature Harappan",
        "Indus Valley",
    ),
]


CRITERIA = [
    "chronological_compatibility",
    "geographical_compatibility",
    "historical_contact_evidence",
    "vocabulary_comparisons",
    "phonological_plausibility",
    "morphological_compatibility",
    "grammatical_compatibility",
    "repeated_sign_sequence_patterns",
    "archaeological_context",
    "independent_validation",
]


# Transparent heuristic priors — analyst may override. Not empirical proof.
DEFAULT_SCORES: dict[str, dict[str, float]] = {
    "h_proto_dravidian": {
        "chronological_compatibility": 0.55,
        "geographical_compatibility": 0.55,
        "historical_contact_evidence": 0.35,
        "vocabulary_comparisons": 0.25,
        "phonological_plausibility": 0.30,
        "morphological_compatibility": 0.25,
        "grammatical_compatibility": 0.20,
        "repeated_sign_sequence_patterns": 0.35,
        "archaeological_context": 0.40,
        "independent_validation": 0.05,
    },
    "h_early_dravidian": {
        "chronological_compatibility": 0.45,
        "geographical_compatibility": 0.50,
        "historical_contact_evidence": 0.30,
        "vocabulary_comparisons": 0.20,
        "phonological_plausibility": 0.25,
        "morphological_compatibility": 0.20,
        "grammatical_compatibility": 0.20,
        "repeated_sign_sequence_patterns": 0.30,
        "archaeological_context": 0.35,
        "independent_validation": 0.05,
    },
    "h_munda": {
        "chronological_compatibility": 0.40,
        "geographical_compatibility": 0.35,
        "historical_contact_evidence": 0.20,
        "vocabulary_comparisons": 0.15,
        "phonological_plausibility": 0.20,
        "morphological_compatibility": 0.15,
        "grammatical_compatibility": 0.15,
        "repeated_sign_sequence_patterns": 0.20,
        "archaeological_context": 0.25,
        "independent_validation": 0.05,
    },
    "h_indo_aryan": {
        "chronological_compatibility": 0.25,
        "geographical_compatibility": 0.40,
        "historical_contact_evidence": 0.20,
        "vocabulary_comparisons": 0.15,
        "phonological_plausibility": 0.15,
        "morphological_compatibility": 0.15,
        "grammatical_compatibility": 0.15,
        "repeated_sign_sequence_patterns": 0.20,
        "archaeological_context": 0.25,
        "independent_validation": 0.05,
    },
    "h_other": {
        "chronological_compatibility": 0.30,
        "geographical_compatibility": 0.30,
        "historical_contact_evidence": 0.15,
        "vocabulary_comparisons": 0.10,
        "phonological_plausibility": 0.10,
        "morphological_compatibility": 0.10,
        "grammatical_compatibility": 0.10,
        "repeated_sign_sequence_patterns": 0.15,
        "archaeological_context": 0.20,
        "independent_validation": 0.05,
    },
    "h_isolate": {
        "chronological_compatibility": 0.60,
        "geographical_compatibility": 0.60,
        "historical_contact_evidence": 0.30,
        "vocabulary_comparisons": 0.10,
        "phonological_plausibility": 0.10,
        "morphological_compatibility": 0.10,
        "grammatical_compatibility": 0.10,
        "repeated_sign_sequence_patterns": 0.25,
        "archaeological_context": 0.45,
        "independent_validation": 0.05,
    },
    "h_nonlinguistic": {
        "chronological_compatibility": 0.70,
        "geographical_compatibility": 0.70,
        "historical_contact_evidence": 0.40,
        "vocabulary_comparisons": 0.05,
        "phonological_plausibility": 0.05,
        "morphological_compatibility": 0.05,
        "grammatical_compatibility": 0.05,
        "repeated_sign_sequence_patterns": 0.45,
        "archaeological_context": 0.55,
        "independent_validation": 0.10,
    },
}


def score_hypotheses(
    overrides: dict[str, dict[str, float]] | None = None,
) -> list[HypothesisScore]:
    scores_map = {k: dict(v) for k, v in DEFAULT_SCORES.items()}
    if overrides:
        for hid, vals in overrides.items():
            scores_map.setdefault(hid, {})
            scores_map[hid].update(vals)

    results: list[HypothesisScore] = []
    for hyp in CANDIDATE_HYPOTHESES:
        s = scores_map.get(hyp.hypothesis_id, {c: 0.1 for c in CRITERIA})
        overall = sum(s.get(c, 0.0) for c in CRITERIA) / len(CRITERIA)
        results.append(
            HypothesisScore(
                hypothesis_id=hyp.hypothesis_id,
                label=hyp.label,
                scores=s,
                overall=overall,
                notes=[
                    hyp.description,
                    f"Chronology: {hyp.chronological_window}",
                    f"Geography: {hyp.geographic_window}",
                    "Independent validation remains near zero for all candidates.",
                    "Do not force a language family onto the evidence.",
                ],
                evidence_tier=EvidenceTier.LINGUISTIC_HYPOTHESIS,
            )
        )
    results.sort(key=lambda x: -x.overall)
    return results
