from hypotheses.speculative_translator import english_to_indus, indus_to_english_hypothesis
from database.db import Database
from ingestion.pipeline import run_ingestion


def test_english_to_indus_labelled(tmp_path):
    db = Database(tmp_path / "t.db")
    run_ingestion(db, include_network_probes=False, include_synthetic=True)
    result = english_to_indus("The merchant sends copper to the city", db)
    assert "SPECULATIVE" in result.banner
    assert result.evidence_tier == "speculative_interpretation"
    assert result.confidence < 0.5
    assert len(result.sign_sequence) >= 3
    assert result.proof["corpus"]["n_indus_inscriptions"] > 0
    # determiners skipped
    skipped = [a for a in result.assignments if a.english_token == "the"]
    assert skipped and skipped[0].skipped


def test_reverse_slots(tmp_path):
    db = Database(tmp_path / "t2.db")
    run_ingestion(db, include_network_probes=False, include_synthetic=True)
    rev = indus_to_english_hypothesis(["IVS001", "IVS002"], db)
    assert "SPECULATIVE" in rev["banner"]
    assert "slots" in rev["speculative_slot_reading"].lower() or "[" in rev["speculative_slot_reading"]
