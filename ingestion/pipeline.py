"""Orchestrate source registry seeding and ingestion."""

from __future__ import annotations

from config.logging_config import setup_logging
from database.db import Database, get_db
from ingestion.egyptian import (
    HuggingFaceEgyptianAdapter,
    SyntheticEgyptianAdapter,
    TLAAdapter,
)
from ingestion.indus import (
    FieldCadyIndusAdapter,
    HuggingFaceIndusAdapter,
    SyntheticIndusAdapter,
)
from ingestion.mesopotamia import (
    CDLIAdapter,
    NaBuCCoAdapter,
    ORACCAdapter,
    SyntheticMesopotamiaAdapter,
)
from ingestion.source_registry import seed_source_registry
from ingestion.synthetic import (
    build_synthetic_corpora,
    build_synthetic_meluhha,
    write_synthetic_files,
)

logger = setup_logging("ingestion.pipeline")


def run_ingestion(
    db: Database | None = None,
    include_network_probes: bool = True,
    include_synthetic: bool = True,
    try_huggingface: bool = False,
) -> dict[str, int]:
    """Run adapters and return counts by civilisation."""
    db = db or get_db()
    seed_source_registry(db)
    write_synthetic_files()

    adapters = []
    if include_network_probes:
        adapters.extend(
            [
                FieldCadyIndusAdapter(db),
                CDLIAdapter(db),
                ORACCAdapter(db),
                NaBuCCoAdapter(db),
                TLAAdapter(db),
            ]
        )
    if try_huggingface:
        adapters.extend(
            [HuggingFaceIndusAdapter(db), HuggingFaceEgyptianAdapter(db)]
        )
    if include_synthetic:
        adapters.extend(
            [
                SyntheticIndusAdapter(db),
                SyntheticMesopotamiaAdapter(db),
                SyntheticEgyptianAdapter(db),
            ]
        )
        # Additional synthetic civilisations not covered by adapters above
        corpora = build_synthetic_corpora()
        for civ in ("linear_b", "proto_dravidian", "munda"):
            for rec in corpora[civ]:
                db.upsert_record(rec)
        for mel in build_synthetic_meluhha():
            db.upsert_meluhha(mel)

    total = 0
    for adapter in adapters:
        logger.info("Running adapter %s", adapter.source_id)
        records = adapter.run()
        total += len(records)

    counts = db.count_by_civilisation()
    logger.info("Ingestion complete. records=%s counts=%s", total, counts)
    return counts


if __name__ == "__main__":
    print(run_ingestion())
