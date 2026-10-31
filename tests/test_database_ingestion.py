from pathlib import Path

from database.db import Database
from database.models import HistoricalRecord
from ingestion.pipeline import run_ingestion
from ingestion.synthetic import build_synthetic_corpora, write_synthetic_files
from historical.trade_network import build_trade_graph
from hypotheses.inference import generate_candidates


def test_synthetic_labelled():
    corpora = build_synthetic_corpora()
    assert all(r.is_synthetic for r in corpora["indus"])
    assert all(r.translation is None for r in corpora["indus"])


def test_db_roundtrip(tmp_path: Path):
    db = Database(tmp_path / "test.db")
    rec = HistoricalRecord(
        record_id="T1",
        civilisation="indus",
        language=None,
        writing_system="indus_script",
        sign_sequence=["A", "B"],
        is_synthetic=True,
        translation_status="none",
    )
    db.upsert_record(rec)
    got = db.get_record("T1")
    assert got is not None
    assert got.sign_sequence == ["A", "B"]


def test_ingestion_and_candidates(tmp_path: Path):
    write_synthetic_files()
    db = Database(tmp_path / "ingest.db")
    counts = run_ingestion(db, include_network_probes=False, include_synthetic=True)
    assert counts.get("indus", 0) > 0
    cands = generate_candidates(db)
    assert isinstance(cands, list)
    g = build_trade_graph()
    assert g.number_of_nodes() > 5
