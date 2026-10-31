"""Data ingestion package."""

from ingestion.pipeline import run_ingestion
from ingestion.source_registry import seed_source_registry

__all__ = ["run_ingestion", "seed_source_registry"]
