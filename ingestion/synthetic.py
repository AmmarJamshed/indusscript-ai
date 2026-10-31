"""SYNTHETIC corpora for software testing only.

These records are clearly labelled and must never be presented as historical
evidence. They exercise normalisation, statistics, Meluhha indexing and the
dashboard when real downloads are unavailable or licence-restricted.
"""

from __future__ import annotations

import json
from pathlib import Path

from config.settings import SYNTHETIC_DIR, ensure_directories
from database.models import (
    EvidenceTier,
    HistoricalRecord,
    MeluhhaEvidence,
    UncertaintyAnnotation,
)

# Small invented inventories — NOT real decipherment catalogues
INDUS_SIGNS = [f"IVS{i:03d}" for i in range(1, 41)]
SUMERIAN_SIGNS = [f"SUM{i:03d}" for i in range(1, 31)]
AKKADIAN_SIGNS = [f"AKK{i:03d}" for i in range(1, 31)]
EGYPTIAN_SIGNS = [f"EGY{i:03d}" for i in range(1, 36)]
LINEARB_SIGNS = [f"LB{i:03d}" for i in range(1, 26)]


def _seq(signs: list[str], pattern: list[int]) -> list[str]:
    return [signs[i % len(signs)] for i in pattern]


def build_synthetic_corpora() -> dict[str, list[HistoricalRecord]]:
    ensure_directories()
    indus = [
        HistoricalRecord(
            record_id="SYNTHETIC-INDUS-001",
            civilisation="indus",
            language=None,
            writing_system="indus_script",
            original_script="indus",
            transliteration=None,
            translation=None,
            sign_sequence=_seq(INDUS_SIGNS, [1, 5, 5, 12, 3]),
            sign_inventory=INDUS_SIGNS[:20],
            reading_direction="RTL",
            date_range="2600-1900 BCE",
            geographical_location="Indus Valley",
            archaeological_site="Mohenjo-daro",
            object_type="seal",
            source_reference="SYNTHETIC",
            confidence=1.0,
            uncertainty_annotations=[
                UncertaintyAnnotation("language", "Undeciphered; language unknown", 0.0)
            ],
            is_synthetic=True,
            translation_status="none",
            metadata={"label": "SYNTHETIC"},
        ),
        HistoricalRecord(
            record_id="SYNTHETIC-INDUS-002",
            civilisation="indus",
            language=None,
            writing_system="indus_script",
            sign_sequence=_seq(INDUS_SIGNS, [1, 5, 8, 12, 3, 7]),
            sign_inventory=INDUS_SIGNS[:20],
            reading_direction="RTL",
            date_range="2600-1900 BCE",
            archaeological_site="Harappa",
            object_type="seal",
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="none",
            uncertainty_annotations=[
                UncertaintyAnnotation("sign_sequence[2]", "Damaged / uncertain", 0.4)
            ],
            metadata={"label": "SYNTHETIC", "uncertain_positions": [2]},
        ),
        HistoricalRecord(
            record_id="SYNTHETIC-INDUS-003",
            civilisation="indus",
            language=None,
            writing_system="indus_script",
            sign_sequence=_seq(INDUS_SIGNS, [2, 9, 9, 14]),
            reading_direction="UNKNOWN",
            archaeological_site="Dholavira",
            object_type="tablet",
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="none",
            metadata={"label": "SYNTHETIC"},
        ),
        HistoricalRecord(
            record_id="SYNTHETIC-INDUS-004",
            civilisation="indus",
            language=None,
            writing_system="indus_script",
            sign_sequence=_seq(INDUS_SIGNS, [1, 5, 5, 12, 3, 18, 4]),
            reading_direction="RTL",
            archaeological_site="Mohenjo-daro",
            object_type="seal",
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="none",
            metadata={"label": "SYNTHETIC"},
        ),
        HistoricalRecord(
            record_id="SYNTHETIC-INDUS-005",
            civilisation="indus",
            language=None,
            writing_system="indus_script",
            sign_sequence=_seq(INDUS_SIGNS, [6, 11, 1, 5, 20]),
            reading_direction="RTL",
            archaeological_site="Lothal",
            object_type="seal",
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="none",
            metadata={"label": "SYNTHETIC"},
        ),
    ]

    # Add more short Indus texts for n-gram / frequency testing
    for i, site in enumerate(
        ["Harappa", "Mohenjo-daro", "Kalibangan", "Rakhigarhi", "Ganweriwala"] * 4
    ):
        pattern = [(i + j * 3) % 30 + 1 for j in range(3 + (i % 4))]
        indus.append(
            HistoricalRecord(
                record_id=f"SYNTHETIC-INDUS-{100 + i:03d}",
                civilisation="indus",
                language=None,
                writing_system="indus_script",
                sign_sequence=_seq(INDUS_SIGNS, pattern),
                reading_direction="RTL" if i % 2 == 0 else "UNKNOWN",
                archaeological_site=site,
                object_type="seal" if i % 3 else "tablet",
                source_reference="SYNTHETIC",
                is_synthetic=True,
                translation_status="none",
                metadata={"label": "SYNTHETIC"},
            )
        )

    sumerian = []
    for i in range(25):
        pattern = [(i + j * 2) % 25 for j in range(5 + (i % 5))]
        sumerian.append(
            HistoricalRecord(
                record_id=f"SYNTHETIC-SUM-{i:03d}",
                civilisation="sumerian",
                language="Sumerian",
                writing_system="cuneiform",
                transliteration=" ".join(_seq(SUMERIAN_SIGNS, pattern)),
                translation="SYNTHETIC administrative gloss — not a real text",
                sign_sequence=_seq(SUMERIAN_SIGNS, pattern),
                reading_direction="LTR",
                date_range="2100-2000 BCE",
                archaeological_site="Ur",
                object_type="tablet",
                source_reference="SYNTHETIC",
                is_synthetic=True,
                translation_status="synthetic",
                metadata={"label": "SYNTHETIC", "genre": "administrative"},
            )
        )

    akkadian = []
    for i in range(25):
        pattern = [(i * 3 + j) % 28 for j in range(6)]
        akkadian.append(
            HistoricalRecord(
                record_id=f"SYNTHETIC-AKK-{i:03d}",
                civilisation="akkadian",
                language="Akkadian",
                writing_system="cuneiform",
                transliteration=" ".join(_seq(AKKADIAN_SIGNS, pattern)),
                translation="SYNTHETIC trade-related gloss — not a real text",
                sign_sequence=_seq(AKKADIAN_SIGNS, pattern),
                reading_direction="LTR",
                date_range="1900-1600 BCE",
                archaeological_site="Sippar",
                object_type="tablet",
                source_reference="SYNTHETIC",
                is_synthetic=True,
                translation_status="synthetic",
                metadata={"label": "SYNTHETIC", "genre": "trade"},
            )
        )

    egyptian = []
    for i in range(25):
        pattern = [(i + j) % 30 for j in range(4 + (i % 3))]
        egyptian.append(
            HistoricalRecord(
                record_id=f"SYNTHETIC-EGY-{i:03d}",
                civilisation="egyptian",
                language="Ancient Egyptian",
                writing_system="egyptian_hieroglyphic",
                transliteration=" ".join(_seq(EGYPTIAN_SIGNS, pattern)),
                translation="SYNTHETIC funerary gloss — not a real text",
                sign_sequence=_seq(EGYPTIAN_SIGNS, pattern),
                reading_direction="RTL",
                date_range="2000-1500 BCE",
                archaeological_site="Thebes",
                object_type="stela",
                source_reference="SYNTHETIC",
                is_synthetic=True,
                translation_status="synthetic",
                metadata={"label": "SYNTHETIC"},
            )
        )

    linearb = []
    for i in range(15):
        pattern = [(i + j * 2) % 20 for j in range(5)]
        linearb.append(
            HistoricalRecord(
                record_id=f"SYNTHETIC-LB-{i:03d}",
                civilisation="linear_b",
                language="Mycenaean Greek",
                writing_system="linear_b",
                transliteration=" ".join(_seq(LINEARB_SIGNS, pattern)),
                translation="SYNTHETIC palace inventory gloss",
                sign_sequence=_seq(LINEARB_SIGNS, pattern),
                reading_direction="LTR",
                date_range="1400-1200 BCE",
                archaeological_site="Knossos",
                object_type="tablet",
                source_reference="SYNTHETIC",
                is_synthetic=True,
                translation_status="synthetic",
                metadata={"label": "SYNTHETIC"},
            )
        )

    # Proto-Dravidian / Munda as reconstructed lexicon stubs (not inscriptions)
    dravidian = [
        HistoricalRecord(
            record_id="SYNTHETIC-PDRV-LEX-001",
            civilisation="proto_dravidian",
            language="Proto-Dravidian (reconstructed)",
            writing_system="reconstructed_lexicon",
            transliteration="*min",
            translation="fish (illustrative reconstruction placeholder)",
            sign_sequence=["*min"],
            source_reference="SYNTHETIC — not a published etymology entry",
            is_synthetic=True,
            translation_status="synthetic",
            confidence=0.2,
            metadata={
                "label": "SYNTHETIC",
                "note": "Replace with cited reconstructions from reputable scholarship",
            },
        ),
        HistoricalRecord(
            record_id="SYNTHETIC-PDRV-LEX-002",
            civilisation="proto_dravidian",
            language="Proto-Dravidian (reconstructed)",
            writing_system="reconstructed_lexicon",
            transliteration="*kaḷ",
            translation="toddy / toddy-related (illustrative placeholder)",
            sign_sequence=["*kaḷ"],
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="synthetic",
            confidence=0.2,
            metadata={"label": "SYNTHETIC"},
        ),
    ]

    munda = [
        HistoricalRecord(
            record_id="SYNTHETIC-MUNDA-LEX-001",
            civilisation="munda",
            language="Munda (illustrative)",
            writing_system="reconstructed_lexicon",
            transliteration="illustrative-lexeme-a",
            translation="SYNTHETIC lexicon stub",
            sign_sequence=["MUNDA_A"],
            source_reference="SYNTHETIC",
            is_synthetic=True,
            translation_status="synthetic",
            confidence=0.1,
            metadata={"label": "SYNTHETIC"},
        )
    ]

    return {
        "indus": indus,
        "sumerian": sumerian,
        "akkadian": akkadian,
        "egyptian": egyptian,
        "linear_b": linearb,
        "proto_dravidian": dravidian,
        "munda": munda,
    }


def build_synthetic_meluhha() -> list[MeluhhaEvidence]:
    """Illustrative Meluhha-themed stubs for UI/pipeline testing.

    These are NOT real tablets. Structure mirrors fields needed for evidence DB.
    """
    return [
        MeluhhaEvidence(
            evidence_id="SYNTHETIC-MEL-001",
            original_text=None,
            transliteration="lu2 me-luh-ha",
            translation="SYNTHETIC: 'man of Meluhha' — illustrative gloss only",
            date="Ur III (illustrative)",
            source_citation="SYNTHETIC placeholder — replace with CDLI/ORACC citation",
            historical_location="Ur (illustrative)",
            named_people=[],
            commodity_references=["illustrative_commodity"],
            confidence=0.1,
            uncertainty="Entirely synthetic for software testing",
            period="Ur III",
            mentions_interpreter=False,
            is_synthetic=True,
            evidence_tier=EvidenceTier.SPECULATIVE_INTERPRETATION,
        ),
        MeluhhaEvidence(
            evidence_id="SYNTHETIC-MEL-002",
            original_text=None,
            transliteration="eme-bal me-luh-ha",
            translation="SYNTHETIC: Meluhhan interpreter — illustrative gloss only",
            date="Old Akkadian / Ur III (illustrative)",
            source_citation="SYNTHETIC placeholder — cite primary publication",
            historical_location="Mesopotamia (illustrative)",
            named_people=[],
            commodity_references=[],
            confidence=0.1,
            uncertainty="Synthetic; Meluhha ≠ proven Indus language identity",
            period="Ur III",
            mentions_interpreter=True,
            is_synthetic=True,
            evidence_tier=EvidenceTier.SPECULATIVE_INTERPRETATION,
        ),
        MeluhhaEvidence(
            evidence_id="SYNTHETIC-MEL-003",
            original_text=None,
            transliteration="dilmun / magan / me-luh-ha trade triad (illustrative)",
            translation="SYNTHETIC: trade-network placeholder linking Dilmun, Magan, Meluhha",
            date="3rd millennium BCE (illustrative)",
            source_citation="SYNTHETIC — replace with published administrative texts",
            historical_location="Persian Gulf / Indus corridor (illustrative)",
            named_people=["SYNTHETIC-merchant"],
            commodity_references=["copper", "carnelian", "timber"],
            confidence=0.1,
            uncertainty="Synthetic aggregation of well-known scholarly themes",
            period="ED / Akkadian / Ur III",
            mentions_interpreter=False,
            is_synthetic=True,
            evidence_tier=EvidenceTier.SPECULATIVE_INTERPRETATION,
        ),
    ]


def write_synthetic_files() -> Path:
    ensure_directories()
    corpora = build_synthetic_corpora()
    out = {
        civ: [r.to_dict() for r in recs] for civ, recs in corpora.items()
    }
    path = SYNTHETIC_DIR / "corpora.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    mel = [m.to_dict() for m in build_synthetic_meluhha()]
    (SYNTHETIC_DIR / "meluhha.json").write_text(
        json.dumps(mel, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return path
