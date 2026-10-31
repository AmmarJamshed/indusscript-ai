"""IndusScript AI entrypoint.

Usage:
    python app.py                 # seed DB + print status
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import argparse

from config.logging_config import setup_logging
from config.settings import DB_PATH, INTEGRITY_NOTICE, ensure_directories
from corpora.loader import build_registry_for_all
from database.db import get_db
from hypotheses.inference import generate_candidates
from ingestion.pipeline import run_ingestion
from reports.generator import export_report

logger = setup_logging("app")


def bootstrap(network: bool = False, report: bool = False) -> None:
    ensure_directories()
    print(INTEGRITY_NOTICE)
    db = get_db()
    counts = run_ingestion(
        db,
        include_network_probes=network,
        include_synthetic=True,
        try_huggingface=False,
    )
    build_registry_for_all(db)
    generate_candidates(db)
    print(f"Database: {DB_PATH}")
    print("Corpus counts:", counts)
    if report:
        paths = export_report(n_perm=100)
        print("Reports:", {k: str(v) for k, v in paths.items()})


def main() -> None:
    parser = argparse.ArgumentParser(description="IndusScript AI")
    parser.add_argument(
        "--network",
        action="store_true",
        help="Probe remote source portals (respectful; no bulk scrape)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Export research report after bootstrap",
    )
    args = parser.parse_args()
    bootstrap(network=args.network, report=args.report)


if __name__ == "__main__":
    main()
