"""Meluhha historical evidence engine.

Important: Meluhha in Mesopotamian sources is not automatically identical to
the language encoded (if any) by the Indus script.
"""

from __future__ import annotations

from database.db import Database, get_db
from database.models import MeluhhaEvidence
from ingestion.synthetic import build_synthetic_meluhha


MELUHHA_CAVEAT = (
    "Mesopotamian references to Meluhha indicate a trade partner, often associated "
    "by scholars with the Indus region, but do not by themselves identify the "
    "language of Indus inscriptions or prove decipherment."
)


def ensure_meluhha_seed(db: Database | None = None) -> int:
    db = db or get_db()
    existing = db.list_meluhha()
    if existing:
        return len(existing)
    for item in build_synthetic_meluhha():
        db.upsert_meluhha(item)
    return len(build_synthetic_meluhha())


def search_meluhha(
    db: Database | None = None,
    *,
    interpreter_only: bool = False,
    period: str | None = None,
    query: str | None = None,
) -> list[MeluhhaEvidence]:
    db = db or get_db()
    ensure_meluhha_seed(db)
    rows = db.list_meluhha()
    out = []
    for r in rows:
        if interpreter_only and not r.mentions_interpreter:
            continue
        if period and period.lower() not in (r.period or "").lower():
            continue
        if query:
            blob = " ".join(
                filter(
                    None,
                    [
                        r.transliteration,
                        r.translation,
                        r.source_citation,
                        r.historical_location,
                        " ".join(r.commodity_references),
                        " ".join(r.named_people),
                    ],
                )
            ).lower()
            if query.lower() not in blob:
                continue
        out.append(r)
    return out


def meluhha_summary(db: Database | None = None) -> dict:
    rows = search_meluhha(db)
    return {
        "research_question": "C",
        "n_evidence": len(rows),
        "n_interpreter_refs": sum(1 for r in rows if r.mentions_interpreter),
        "n_synthetic": sum(1 for r in rows if r.is_synthetic),
        "periods": sorted({r.period for r in rows if r.period}),
        "commodities": sorted(
            {c for r in rows for c in r.commodity_references}
        ),
        "caveat": MELUHHA_CAVEAT,
        "items": [r.to_dict() for r in rows],
    }
