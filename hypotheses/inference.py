"""Decipherment hypothesis generator.

Produces candidate interpretations explicitly marked as speculative.
Never emits English translations as established facts.
"""

from __future__ import annotations

from collections import Counter

from database.db import Database, get_db
from database.models import CandidateInterpretation, EvidenceTier
from analysis.ngrams import repeated_sequences


def generate_candidates(
    db: Database | None = None,
    candidate_language: str = "Proto-Dravidian",
    max_candidates: int = 10,
) -> list[CandidateInterpretation]:
    db = db or get_db()
    indus = db.get_records(civilisation="indus")
    sequences = [r.sign_sequence for r in indus if r.sign_sequence]
    if not sequences:
        return []

    repeated = repeated_sequences(sequences, min_n=2, max_n=3, min_count=2)
    # Map n-gram -> example inscription
    seq_to_rec = {}
    for rec in indus:
        seq_to_rec[tuple(rec.sign_sequence)] = rec

    candidates: list[CandidateInterpretation] = []
    for i, item in enumerate(repeated[:max_candidates]):
        gram = item["sequence"]
        # Find an inscription containing this gram
        host = None
        for rec in indus:
            s = rec.sign_sequence
            for j in range(len(s) - len(gram) + 1):
                if s[j : j + len(gram)] == gram:
                    host = rec
                    break
            if host:
                break
        if not host:
            continue

        interp = CandidateInterpretation(
            interpretation_id=f"CAND-{i+1:03d}",
            inscription_id=host.record_id,
            sign_sequence=list(gram),
            archaeological_context=(
                f"site={host.archaeological_site}; object={host.object_type}; "
                f"date={host.date_range}"
            ),
            proposed_structure="Possible formulaic / morphological segment (unproven)",
            candidate_language=candidate_language,
            reconstructed_vocabulary=[
                "SYNTHETIC/PLACEHOLDER — cite published reconstructions only"
            ],
            correspondence_explanation=(
                f"Sequence {gram} recurs {item['count']} times. "
                "A candidate reading would require independently justified "
                "sign-to-sound or sign-to-meaning mappings, which are not established."
            ),
            alternative_explanations=[
                "Administrative / non-linguistic mark sequence",
                "Personal name / title formula without recoverable phonology",
                "Chance repetition in a small corpus",
                "Different language family hypothesis",
            ],
            held_out_test_result=(
                "Not validated: no held-out semantic labels exist for Indus."
            ),
            contradictions=[
                "No bilingual key comparable to Rosetta Stone is available.",
                "Short inscription lengths limit morphological tests.",
                "Meluhha references do not supply an Indus signary key.",
            ],
            confidence=min(0.25, 0.05 + 0.02 * item["count"]),
            evidence_tier=EvidenceTier.SPECULATIVE_INTERPRETATION,
            assumptions=[
                "Assumption: recurring sequences are linguistic (unproven).",
                f"Assumption: candidate language = {candidate_language} (unproven).",
                "Assumption: sign order reflects spoken order (direction may be uncertain).",
            ],
            is_synthetic=host.is_synthetic,
        )
        candidates.append(interp)
        db.upsert_interpretation(interp)

    return candidates


def interpretation_report(db: Database | None = None) -> dict:
    db = db or get_db()
    items = db.list_interpretations()
    if not items:
        items = generate_candidates(db)
    return {
        "research_question": "D",
        "n_candidates": len(items),
        "candidates": [c.to_dict() for c in items],
        "integrity": (
            "All readings are hypotheses. Observed facts are limited to attested "
            "sign sequences and archaeological metadata. No English gloss is an "
            "established translation of Indus."
        ),
    }
