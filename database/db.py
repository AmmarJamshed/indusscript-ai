"""SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from config.settings import DB_PATH, ensure_directories
from database.models import (
    CandidateInterpretation,
    DownloadStatus,
    EvidenceTier,
    HistoricalRecord,
    MeluhhaEvidence,
    SourceRegistryEntry,
    UncertaintyAnnotation,
)
from database.schema import SCHEMA_SQL


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: Path | str | None = None) -> None:
        ensure_directories()
        self.path = Path(path) if path else DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)

    # --- sources ---
    def upsert_source(self, entry: SourceRegistryEntry) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO sources (
                    source_id, name, url, civilisation, format, licence,
                    redistribution_ok, api_limitations, availability,
                    download_status, data_quality, notes, last_checked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    name=excluded.name,
                    url=excluded.url,
                    civilisation=excluded.civilisation,
                    format=excluded.format,
                    licence=excluded.licence,
                    redistribution_ok=excluded.redistribution_ok,
                    api_limitations=excluded.api_limitations,
                    availability=excluded.availability,
                    download_status=excluded.download_status,
                    data_quality=excluded.data_quality,
                    notes=excluded.notes,
                    last_checked=excluded.last_checked
                """,
                (
                    entry.source_id,
                    entry.name,
                    entry.url,
                    entry.civilisation,
                    entry.format,
                    entry.licence,
                    int(entry.redistribution_ok),
                    entry.api_limitations,
                    entry.availability,
                    entry.download_status.value
                    if isinstance(entry.download_status, DownloadStatus)
                    else entry.download_status,
                    entry.data_quality,
                    entry.notes,
                    entry.last_checked or _utc_now(),
                ),
            )

    def list_sources(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM sources ORDER BY source_id").fetchall()
        return [dict(r) for r in rows]

    # --- records ---
    def upsert_record(self, record: HistoricalRecord) -> None:
        # Integrity: never store invented Indus translations as attested facts
        translation = record.translation
        translation_status = record.translation_status
        if record.civilisation == "indus" and translation and translation_status == "none":
            translation_status = "hypothesis"

        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO records (
                    record_id, civilisation, language, writing_system, original_script,
                    transliteration, translation, sign_sequence, sign_inventory,
                    reading_direction, date_range, geographical_location,
                    archaeological_site, object_type, source_reference, image_reference,
                    confidence, uncertainty_annotations, is_synthetic, translation_status,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    civilisation=excluded.civilisation,
                    language=excluded.language,
                    writing_system=excluded.writing_system,
                    original_script=excluded.original_script,
                    transliteration=excluded.transliteration,
                    translation=excluded.translation,
                    sign_sequence=excluded.sign_sequence,
                    sign_inventory=excluded.sign_inventory,
                    reading_direction=excluded.reading_direction,
                    date_range=excluded.date_range,
                    geographical_location=excluded.geographical_location,
                    archaeological_site=excluded.archaeological_site,
                    object_type=excluded.object_type,
                    source_reference=excluded.source_reference,
                    image_reference=excluded.image_reference,
                    confidence=excluded.confidence,
                    uncertainty_annotations=excluded.uncertainty_annotations,
                    is_synthetic=excluded.is_synthetic,
                    translation_status=excluded.translation_status,
                    metadata=excluded.metadata
                """,
                (
                    record.record_id,
                    record.civilisation,
                    record.language,
                    record.writing_system,
                    record.original_script,
                    record.transliteration,
                    translation,
                    json.dumps(record.sign_sequence),
                    json.dumps(record.sign_inventory),
                    record.reading_direction,
                    record.date_range,
                    record.geographical_location,
                    record.archaeological_site,
                    record.object_type,
                    record.source_reference,
                    record.image_reference,
                    record.confidence,
                    json.dumps(
                        [
                            a.__dict__ if isinstance(a, UncertaintyAnnotation) else a
                            for a in record.uncertainty_annotations
                        ]
                    ),
                    int(record.is_synthetic),
                    translation_status,
                    json.dumps(record.metadata),
                ),
            )

    def get_records(
        self,
        civilisation: str | None = None,
        site: str | None = None,
        include_synthetic: bool = True,
    ) -> list[HistoricalRecord]:
        clauses: list[str] = []
        params: list[Any] = []
        if civilisation:
            clauses.append("civilisation = ?")
            params.append(civilisation)
        if site:
            clauses.append("archaeological_site = ?")
            params.append(site)
        if not include_synthetic:
            clauses.append("is_synthetic = 0")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM records {where} ORDER BY record_id", params
            ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_record(self, record_id: str) -> HistoricalRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM records WHERE record_id = ?", (record_id,)
            ).fetchone()
        return self._row_to_record(row) if row else None

    def count_by_civilisation(self) -> dict[str, int]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT civilisation, COUNT(*) AS n FROM records GROUP BY civilisation"
            ).fetchall()
        return {r["civilisation"]: r["n"] for r in rows}

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> HistoricalRecord:
        data = dict(row)
        data["sign_sequence"] = json.loads(data.get("sign_sequence") or "[]")
        data["sign_inventory"] = json.loads(data.get("sign_inventory") or "[]")
        data["uncertainty_annotations"] = json.loads(
            data.get("uncertainty_annotations") or "[]"
        )
        data["metadata"] = json.loads(data.get("metadata") or "{}")
        data["is_synthetic"] = bool(data.get("is_synthetic"))
        return HistoricalRecord.from_dict(data)

    # --- raw payloads ---
    def store_raw_payload(
        self,
        payload_id: str,
        source_id: str,
        original_identifier: str,
        content_type: str,
        raw_json: dict[str, Any],
        licence_note: str | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO raw_payloads (
                    payload_id, source_id, original_identifier, retrieved_at,
                    content_type, raw_json, licence_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(payload_id) DO UPDATE SET
                    raw_json=excluded.raw_json,
                    retrieved_at=excluded.retrieved_at
                """,
                (
                    payload_id,
                    source_id,
                    original_identifier,
                    _utc_now(),
                    content_type,
                    json.dumps(raw_json),
                    licence_note,
                ),
            )

    # --- Meluhha ---
    def upsert_meluhha(self, evidence: MeluhhaEvidence) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO meluhha_evidence (
                    evidence_id, original_text, transliteration, translation, date,
                    source_citation, historical_location, named_people,
                    commodity_references, confidence, uncertainty, period,
                    mentions_interpreter, is_synthetic, evidence_tier
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    original_text=excluded.original_text,
                    transliteration=excluded.transliteration,
                    translation=excluded.translation,
                    date=excluded.date,
                    source_citation=excluded.source_citation,
                    historical_location=excluded.historical_location,
                    named_people=excluded.named_people,
                    commodity_references=excluded.commodity_references,
                    confidence=excluded.confidence,
                    uncertainty=excluded.uncertainty,
                    period=excluded.period,
                    mentions_interpreter=excluded.mentions_interpreter,
                    is_synthetic=excluded.is_synthetic,
                    evidence_tier=excluded.evidence_tier
                """,
                (
                    evidence.evidence_id,
                    evidence.original_text,
                    evidence.transliteration,
                    evidence.translation,
                    evidence.date,
                    evidence.source_citation,
                    evidence.historical_location,
                    json.dumps(evidence.named_people),
                    json.dumps(evidence.commodity_references),
                    evidence.confidence,
                    evidence.uncertainty,
                    evidence.period,
                    int(evidence.mentions_interpreter),
                    int(evidence.is_synthetic),
                    evidence.evidence_tier.value
                    if isinstance(evidence.evidence_tier, EvidenceTier)
                    else evidence.evidence_tier,
                ),
            )

    def list_meluhha(self) -> list[MeluhhaEvidence]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM meluhha_evidence ORDER BY evidence_id"
            ).fetchall()
        out: list[MeluhhaEvidence] = []
        for r in rows:
            d = dict(r)
            out.append(
                MeluhhaEvidence(
                    evidence_id=d["evidence_id"],
                    original_text=d["original_text"],
                    transliteration=d["transliteration"],
                    translation=d["translation"],
                    date=d["date"],
                    source_citation=d["source_citation"],
                    historical_location=d["historical_location"],
                    named_people=json.loads(d["named_people"] or "[]"),
                    commodity_references=json.loads(d["commodity_references"] or "[]"),
                    confidence=d["confidence"] or 0.0,
                    uncertainty=d["uncertainty"] or "",
                    period=d["period"],
                    mentions_interpreter=bool(d["mentions_interpreter"]),
                    is_synthetic=bool(d["is_synthetic"]),
                    evidence_tier=EvidenceTier(d["evidence_tier"])
                    if d["evidence_tier"]
                    else EvidenceTier.LINGUISTIC_HYPOTHESIS,
                )
            )
        return out

    # --- interpretations ---
    def upsert_interpretation(self, item: CandidateInterpretation) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO interpretations (
                    interpretation_id, inscription_id, sign_sequence,
                    archaeological_context, proposed_structure, candidate_language,
                    reconstructed_vocabulary, correspondence_explanation,
                    alternative_explanations, held_out_test_result, contradictions,
                    confidence, evidence_tier, assumptions, is_synthetic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(interpretation_id) DO UPDATE SET
                    inscription_id=excluded.inscription_id,
                    sign_sequence=excluded.sign_sequence,
                    archaeological_context=excluded.archaeological_context,
                    proposed_structure=excluded.proposed_structure,
                    candidate_language=excluded.candidate_language,
                    reconstructed_vocabulary=excluded.reconstructed_vocabulary,
                    correspondence_explanation=excluded.correspondence_explanation,
                    alternative_explanations=excluded.alternative_explanations,
                    held_out_test_result=excluded.held_out_test_result,
                    contradictions=excluded.contradictions,
                    confidence=excluded.confidence,
                    evidence_tier=excluded.evidence_tier,
                    assumptions=excluded.assumptions,
                    is_synthetic=excluded.is_synthetic
                """,
                (
                    item.interpretation_id,
                    item.inscription_id,
                    json.dumps(item.sign_sequence),
                    item.archaeological_context,
                    item.proposed_structure,
                    item.candidate_language,
                    json.dumps(item.reconstructed_vocabulary),
                    item.correspondence_explanation,
                    json.dumps(item.alternative_explanations),
                    item.held_out_test_result,
                    json.dumps(item.contradictions),
                    item.confidence,
                    item.evidence_tier.value
                    if isinstance(item.evidence_tier, EvidenceTier)
                    else item.evidence_tier,
                    json.dumps(item.assumptions),
                    int(item.is_synthetic),
                ),
            )

    def list_interpretations(self) -> list[CandidateInterpretation]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM interpretations ORDER BY confidence DESC"
            ).fetchall()
        out: list[CandidateInterpretation] = []
        for r in rows:
            d = dict(r)
            out.append(
                CandidateInterpretation(
                    interpretation_id=d["interpretation_id"],
                    inscription_id=d["inscription_id"],
                    sign_sequence=json.loads(d["sign_sequence"] or "[]"),
                    archaeological_context=d["archaeological_context"],
                    proposed_structure=d["proposed_structure"],
                    candidate_language=d["candidate_language"],
                    reconstructed_vocabulary=json.loads(
                        d["reconstructed_vocabulary"] or "[]"
                    ),
                    correspondence_explanation=d["correspondence_explanation"] or "",
                    alternative_explanations=json.loads(
                        d["alternative_explanations"] or "[]"
                    ),
                    held_out_test_result=d["held_out_test_result"],
                    contradictions=json.loads(d["contradictions"] or "[]"),
                    confidence=d["confidence"] or 0.0,
                    evidence_tier=EvidenceTier(d["evidence_tier"])
                    if d["evidence_tier"]
                    else EvidenceTier.SPECULATIVE_INTERPRETATION,
                    assumptions=json.loads(d["assumptions"] or "[]"),
                    is_synthetic=bool(d["is_synthetic"]),
                )
            )
        return out

    def cache_set(self, key: str, payload: dict[str, Any]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO analysis_cache (cache_key, created_at, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    created_at=excluded.created_at,
                    payload=excluded.payload
                """,
                (key, _utc_now(), json.dumps(payload)),
            )

    def cache_get(self, key: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT payload FROM analysis_cache WHERE cache_key = ?", (key,)
            ).fetchone()
        return json.loads(row["payload"]) if row else None


def get_db(path: Path | str | None = None) -> Database:
    return Database(path)
