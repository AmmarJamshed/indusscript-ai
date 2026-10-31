"""Load normalised corpora from the database."""

from __future__ import annotations

from database.db import Database, get_db
from database.models import HistoricalRecord
from normalisation.signs import MappingRegistry, build_default_registry_from_sequences, normalise_sequence


def load_sequences(
    civilisation: str,
    db: Database | None = None,
    include_synthetic: bool = True,
    reverse: bool = False,
) -> list[list[str]]:
    db = db or get_db()
    records = db.get_records(civilisation=civilisation, include_synthetic=include_synthetic)
    seqs = [r.sign_sequence for r in records if r.sign_sequence]
    vocab = build_default_registry_from_sequences(civilisation, seqs)
    return [
        normalise_sequence(s, vocab, force_reverse=reverse)
        for s in seqs
    ]


def load_records(
    civilisation: str | None = None,
    db: Database | None = None,
    include_synthetic: bool = True,
) -> list[HistoricalRecord]:
    db = db or get_db()
    return db.get_records(civilisation=civilisation, include_synthetic=include_synthetic)


def build_registry_for_all(db: Database | None = None) -> MappingRegistry:
    db = db or get_db()
    registry = MappingRegistry()
    counts = db.count_by_civilisation()
    for civ in counts:
        seqs = [r.sign_sequence for r in db.get_records(civilisation=civ)]
        vocab = build_default_registry_from_sequences(civ, seqs)
        registry.vocabularies[civ] = vocab
    registry.save()
    return registry
