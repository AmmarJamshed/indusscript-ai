"""Speculative English ↔ Indus sign lab.

IMPORTANT: Outputs are labelled SPECULATIVE. They are not a decipherment.
Mappings combine (1) analyst-chosen concept frames, (2) corpus frequency /
n-gram / positional statistics, and (3) comparative structural similarity
scores. None of this proves phonetic or semantic values for Indus signs.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from analysis.frequency import frequency_report, js_divergence, sign_frequencies
from analysis.ngrams import extract_ngrams, repeated_sequences
from analysis.positional import positional_probabilities
from analysis.sequence_analysis import compare_corpora
from corpora.loader import load_sequences
from database.db import Database, get_db
from database.models import EvidenceTier

SPECULATIVE_BANNER = (
    "SPECULATIVE ASSUMED TRANSLATION — not independently verified. "
    "Indus remains undeciphered. Similarity is not shared meaning."
)

# Transparent heuristic concept frames (NOT established Indus readings).
# Each concept prefers signs that are frequent / boundary-enriched in the corpus.
CONCEPT_LEXICON: dict[str, dict] = {
    "king": {
        "gloss_frame": "ruler / authority (administrative hypothesis)",
        "proto_dravidian_placeholder": "*kō / *mann- (illustrative only)",
        "semantic_tags": ["authority", "person"],
        "prefer_position": "beginning",
    },
    "ruler": {
        "gloss_frame": "ruler / authority (administrative hypothesis)",
        "proto_dravidian_placeholder": "*kō (illustrative only)",
        "semantic_tags": ["authority", "person"],
        "prefer_position": "beginning",
    },
    "merchant": {
        "gloss_frame": "trader / Meluhha-contact trade frame",
        "proto_dravidian_placeholder": "unassigned — trade title hypothesis",
        "semantic_tags": ["trade", "person"],
        "prefer_position": "beginning",
    },
    "trader": {
        "gloss_frame": "trader / Meluhha-contact trade frame",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["trade", "person"],
        "prefer_position": "beginning",
    },
    "fish": {
        "gloss_frame": "fish / aquatic commodity (iconographic + Dravidian *min hypothesis)",
        "proto_dravidian_placeholder": "*min (published reconstruction exists for 'fish'; Indus link unproven)",
        "semantic_tags": ["commodity", "animal"],
        "prefer_position": "middle",
    },
    "grain": {
        "gloss_frame": "grain / staple commodity (admin seal hypothesis)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["commodity"],
        "prefer_position": "middle",
    },
    "copper": {
        "gloss_frame": "copper / Magan–Dilmun trade commodity frame",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["commodity", "trade"],
        "prefer_position": "middle",
    },
    "seal": {
        "gloss_frame": "ownership / control mark (terminal jar/control hypothesis)",
        "proto_dravidian_placeholder": "non-linguistic terminal mark possible",
        "semantic_tags": ["formula", "control"],
        "prefer_position": "ending",
    },
    "owner": {
        "gloss_frame": "owner / possessive formula",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["person", "formula"],
        "prefer_position": "beginning",
    },
    "god": {
        "gloss_frame": "deity / ritual frame (highly speculative)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["ritual"],
        "prefer_position": "beginning",
    },
    "city": {
        "gloss_frame": "place / settlement name frame",
        "proto_dravidian_placeholder": "unassigned toponym",
        "semantic_tags": ["place"],
        "prefer_position": "middle",
    },
    "harappa": {
        "gloss_frame": "place-name frame (Harappa)",
        "proto_dravidian_placeholder": "toponym — not a phonetic Indus reading",
        "semantic_tags": ["place"],
        "prefer_position": "middle",
    },
    "mohenjo": {
        "gloss_frame": "place-name frame (Mohenjo-daro)",
        "proto_dravidian_placeholder": "toponym — not a phonetic Indus reading",
        "semantic_tags": ["place"],
        "prefer_position": "middle",
    },
    "daro": {
        "gloss_frame": "place-name frame (Mohenjo-daro)",
        "proto_dravidian_placeholder": "toponym",
        "semantic_tags": ["place"],
        "prefer_position": "middle",
    },
    "give": {
        "gloss_frame": "transfer / delivery verb (admin hypothesis)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["verb", "trade"],
        "prefer_position": "middle",
    },
    "send": {
        "gloss_frame": "dispatch / shipment verb (trade hypothesis)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["verb", "trade"],
        "prefer_position": "middle",
    },
    "receive": {
        "gloss_frame": "receipt verb (admin hypothesis)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["verb", "trade"],
        "prefer_position": "middle",
    },
    "man": {
        "gloss_frame": "person / human referent",
        "proto_dravidian_placeholder": "*āḷ / *man (illustrative only)",
        "semantic_tags": ["person"],
        "prefer_position": "beginning",
    },
    "woman": {
        "gloss_frame": "person / human referent",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["person"],
        "prefer_position": "beginning",
    },
    "water": {
        "gloss_frame": "water / river commodity or place frame",
        "proto_dravidian_placeholder": "*nīr (illustrative only)",
        "semantic_tags": ["commodity", "place"],
        "prefer_position": "middle",
    },
    "boat": {
        "gloss_frame": "vessel / maritime trade frame (Dilmun–Meluhha)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["trade", "transport"],
        "prefer_position": "middle",
    },
    "temple": {
        "gloss_frame": "institution / ritual building (speculative)",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["ritual", "place"],
        "prefer_position": "beginning",
    },
    "offering": {
        "gloss_frame": "dedication / offering formula",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["ritual", "formula"],
        "prefer_position": "ending",
    },
    "of": {
        "gloss_frame": "relational / genitive particle hypothesis",
        "proto_dravidian_placeholder": "case marker hypothesis (unproven)",
        "semantic_tags": ["grammar"],
        "prefer_position": "middle",
    },
    "the": {
        "gloss_frame": "(ignored determiner — English-only)",
        "proto_dravidian_placeholder": "—",
        "semantic_tags": ["skip"],
        "prefer_position": "middle",
    },
    "a": {
        "gloss_frame": "(ignored determiner — English-only)",
        "proto_dravidian_placeholder": "—",
        "semantic_tags": ["skip"],
        "prefer_position": "middle",
    },
    "an": {
        "gloss_frame": "(ignored determiner — English-only)",
        "proto_dravidian_placeholder": "—",
        "semantic_tags": ["skip"],
        "prefer_position": "middle",
    },
    "to": {
        "gloss_frame": "directional / dative hypothesis",
        "proto_dravidian_placeholder": "case marker hypothesis (unproven)",
        "semantic_tags": ["grammar"],
        "prefer_position": "middle",
    },
    "from": {
        "gloss_frame": "ablative / source hypothesis",
        "proto_dravidian_placeholder": "case marker hypothesis (unproven)",
        "semantic_tags": ["grammar"],
        "prefer_position": "middle",
    },
    "and": {
        "gloss_frame": "coordinator hypothesis",
        "proto_dravidian_placeholder": "unassigned",
        "semantic_tags": ["grammar"],
        "prefer_position": "middle",
    },
}


@dataclass
class SignAssignment:
    english_token: str
    role: str
    assumed_gloss_frame: str
    reconstructed_placeholder: str
    assigned_sign: str | None
    sign_rank: int | None
    sign_frequency: int
    position_preference: str
    evidence_notes: list[str] = field(default_factory=list)
    skipped: bool = False


@dataclass
class SpeculativeTranslation:
    english_sentence: str
    assumed_language_frame: str
    reading_direction: str
    sign_sequence: list[str]
    display_line: str
    assignments: list[SignAssignment]
    confidence: float
    evidence_tier: str
    proof: dict
    assumptions: list[str]
    limitations: list[str]
    banner: str = SPECULATIVE_BANNER

    def to_dict(self) -> dict:
        data = asdict(self)
        return data


def _tokenize(sentence: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", sentence.lower())


def _corpus_stats(db: Database) -> dict:
    indus_seqs = load_sequences("indus", db)
    freq = sign_frequencies(indus_seqs)
    ranked = [s for s, _ in freq.most_common()]
    pos = positional_probabilities(indus_seqs)
    repeated = repeated_sequences(indus_seqs, min_n=2, max_n=3, min_count=2)[:15]
    freq_report = frequency_report(indus_seqs)

    comparisons = {}
    for civ in ("sumerian", "akkadian", "egyptian"):
        other = load_sequences(civ, db)
        if other and indus_seqs:
            comparisons[civ] = {
                "js_divergence": js_divergence(freq, sign_frequencies(other)),
                "note": "Lower JS = more similar frequency structure (question B only).",
            }

    return {
        "indus_seqs": indus_seqs,
        "freq": freq,
        "ranked": ranked,
        "pos": pos,
        "repeated": repeated,
        "freq_report": freq_report,
        "comparisons": comparisons,
        "inventory_size": len(freq),
        "n_inscriptions": len(indus_seqs),
    }


def _pick_sign(
    concept: dict,
    ranked: list[str],
    freq,
    pos: dict,
    used: set[str],
    token_index: int,
) -> tuple[str | None, int | None, int, list[str]]:
    if not ranked:
        return None, None, 0, ["No Indus inventory available."]

    prefer = concept.get("prefer_position", "middle")
    pos_scores = pos.get(prefer, {})
    # Rank candidates: high positional preference, not yet used, then global frequency
    candidates = []
    for rank, sign in enumerate(ranked, start=1):
        if sign in used:
            continue
        score = pos_scores.get(sign, 0.0) * 2.0 + (1.0 / rank)
        candidates.append((score, rank, sign))
    if not candidates:
        # reuse allowed if inventory exhausted
        sign = ranked[token_index % len(ranked)]
        rank = ranked.index(sign) + 1
        return sign, rank, int(freq[sign]), [
            "Inventory exhausted; reused a frequent sign (weak heuristic)."
        ]

    candidates.sort(key=lambda x: -x[0])
    score, rank, sign = candidates[0]
    notes = [
        f"Selected by corpus frequency rank #{rank} (count={freq[sign]}).",
        f"Preferred position bucket '{prefer}' weight={pos_scores.get(sign, 0.0):.3f}.",
        "Sign identity is a HEURISTIC stand-in — not a proven phonetic value.",
    ]
    return sign, rank, int(freq[sign]), notes


def english_to_indus(
    sentence: str,
    db: Database | None = None,
    language_frame: str = "Proto-Dravidian (assumed)",
    reading_direction: str = "RTL",
) -> SpeculativeTranslation:
    db = db or get_db()
    stats = _corpus_stats(db)
    tokens = _tokenize(sentence)
    assignments: list[SignAssignment] = []
    used: set[str] = set()
    signs: list[str] = []

    content_i = 0
    for tok in tokens:
        concept = CONCEPT_LEXICON.get(tok)
        if concept and "skip" in concept.get("semantic_tags", []):
            assignments.append(
                SignAssignment(
                    english_token=tok,
                    role="English determiner (no Indus sign assigned)",
                    assumed_gloss_frame=concept["gloss_frame"],
                    reconstructed_placeholder=concept["proto_dravidian_placeholder"],
                    assigned_sign=None,
                    sign_rank=None,
                    sign_frequency=0,
                    position_preference=concept["prefer_position"],
                    evidence_notes=["Determiners are English-structure; skipped."],
                    skipped=True,
                )
            )
            continue

        if not concept:
            # Unknown word: still assign a mid-frequency sign as "unmapped lemma"
            concept = {
                "gloss_frame": f"unmapped English lemma '{tok}' (placeholder sign)",
                "proto_dravidian_placeholder": "no lexicon entry — speculative filler",
                "semantic_tags": ["unknown"],
                "prefer_position": "middle",
            }

        sign, rank, count, notes = _pick_sign(
            concept, stats["ranked"], stats["freq"], stats["pos"], used, content_i
        )
        if sign:
            used.add(sign)
            signs.append(sign)
        assignments.append(
            SignAssignment(
                english_token=tok,
                role=", ".join(concept.get("semantic_tags", [])),
                assumed_gloss_frame=concept["gloss_frame"],
                reconstructed_placeholder=concept["proto_dravidian_placeholder"],
                assigned_sign=sign,
                sign_rank=rank,
                sign_frequency=count,
                position_preference=concept["prefer_position"],
                evidence_notes=notes,
                skipped=False,
            )
        )
        content_i += 1

    # Optional formulaic ending: if corpus often ends with a high-frequency boundary sign
    # and sentence looks administrative, append most common ending sign if not present
    ending_prefs = list(stats["pos"].get("ending", {}).keys())
    if signs and ending_prefs and ending_prefs[0] not in signs:
        # only suggest, do not auto-append unless sentence has seal/offering
        pass

    display_signs = list(reversed(signs)) if reading_direction == "RTL" else list(signs)
    # Confidence: tiny, scaled by how many tokens had lexicon entries
    known = sum(1 for a in assignments if not a.skipped and a.english_token in CONCEPT_LEXICON)
    total = sum(1 for a in assignments if not a.skipped) or 1
    confidence = min(0.22, 0.05 + 0.12 * (known / total))

    # Structural proof block
    ngram_support = []
    if len(signs) >= 2:
        bigrams = extract_ngrams(stats["indus_seqs"], 2)
        for i in range(len(signs) - 1):
            bg = (signs[i], signs[i + 1])
            ngram_support.append(
                {
                    "bigram": list(bg),
                    "attested_count_in_corpus": int(bigrams.get(bg, 0)),
                    "status": "attested" if bigrams.get(bg, 0) else "not attested in corpus",
                }
            )

    proof = {
        "research_questions_used": {
            "B": "Sign chosen via frequency + positional structure of Indus corpus",
            "C": "Trade/Meluhha frames used only as contact context, not language ID",
            "D": "English glosses are assumed hypothesis frames only",
        },
        "corpus": {
            "n_indus_inscriptions": stats["n_inscriptions"],
            "inventory_size": stats["inventory_size"],
            "top_10_signs": stats["freq_report"]["top_20"][:10],
            "recurring_sequences_sample": stats["repeated"][:8],
        },
        "comparative_js_divergence": stats["comparisons"],
        "bigram_attestation": ngram_support,
        "method": (
            "1) Parse English tokens. 2) Look up speculative concept frames. "
            "3) Assign unused high-frequency Indus signs weighted by preferred "
            "position statistics. 4) Report attestation of resulting bigrams."
        ),
    }

    return SpeculativeTranslation(
        english_sentence=sentence,
        assumed_language_frame=language_frame,
        reading_direction=reading_direction,
        sign_sequence=display_signs,
        display_line=" ".join(display_signs) if display_signs else "(no signs assigned)",
        assignments=assignments,
        confidence=confidence,
        evidence_tier=EvidenceTier.SPECULATIVE_INTERPRETATION.value,
        proof=proof,
        assumptions=[
            f"Assumed language frame: {language_frame}",
            f"Assumed reading direction for display: {reading_direction}",
            "Assumed that Indus signs encode language (may be partly non-linguistic).",
            "Assumed concept→sign links from lexicon frames + corpus frequency heuristics.",
            "Reconstructed vocabulary placeholders are NOT proven Indus phonetics.",
        ],
        limitations=[
            "No bilingual key exists for Indus.",
            "Corpus may be synthetic/partial depending on ingestion status.",
            "English word order ≠ Indus word order; RTL display is a convention choice.",
            "Comparative JS divergence measures structure, not translation accuracy.",
            "This output must never be cited as a decipherment.",
        ],
    )


def indus_to_english_hypothesis(
    signs: list[str],
    db: Database | None = None,
    language_frame: str = "Proto-Dravidian (assumed)",
) -> dict:
    """Reverse direction: speculative gloss from a sign sequence."""
    db = db or get_db()
    stats = _corpus_stats(db)
    # Map top signs to a rotating set of high-level frames for readability
    frames = [
        "person/authority?",
        "commodity?",
        "place?",
        "formula/control-mark?",
        "verb/relation?",
    ]
    ranked = stats["ranked"]
    gloss_parts = []
    proof_rows = []
    for i, sign in enumerate(signs):
        rank = ranked.index(sign) + 1 if sign in ranked else None
        frame = frames[i % len(frames)]
        gloss_parts.append(f"[{frame}]")
        proof_rows.append(
            {
                "sign": sign,
                "corpus_rank": rank,
                "frequency": int(stats["freq"].get(sign, 0)),
                "assumed_slot": frame,
            }
        )
    sentence = " ".join(gloss_parts) + "  (slots only — not real English)"
    return {
        "banner": SPECULATIVE_BANNER,
        "input_signs": signs,
        "assumed_language_frame": language_frame,
        "speculative_slot_reading": sentence,
        "readable_summary": (
            "The system will not invent a fluent English sentence as fact. "
            "Instead it shows ordered semantic *slots* suggested by position "
            "and frequency structure."
        ),
        "sign_rows": proof_rows,
        "confidence": 0.08,
        "evidence_tier": EvidenceTier.SPECULATIVE_INTERPRETATION.value,
    }
