"""Indus corpus adapters.

Attempts legitimate public retrieval where possible. Falls back to documenting
unavailability — never invents historical inscriptions.
"""

from __future__ import annotations

import json
from pathlib import Path

from config.logging_config import setup_logging
from config.settings import SYNTHETIC_DIR
from database.models import DownloadStatus, HistoricalRecord
from ingestion.base import BaseAdapter
from ingestion.synthetic import build_synthetic_corpora

logger = setup_logging("ingestion.indus")


class FieldCadyIndusAdapter(BaseAdapter):
    source_id = "field_cady_indus"

    def fetch(self) -> list[HistoricalRecord]:
        # Probe GitHub API for repo metadata only; do not invent corpus rows.
        url = "https://api.github.com/repos/field-cady/indus_valley_script_corpus"
        try:
            resp = self.http_get(url)
            meta = resp.json()
            self.save_raw("repo_meta.json", meta)
            self.mark_status(
                DownloadStatus.PARTIAL,
                "Repository reachable; full corpus download requires licence review "
                "and explicit clone. Not auto-mirrored.",
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("field-cady probe failed: %s", exc)
            self.mark_status(DownloadStatus.UNAVAILABLE, str(exc))
        return []


class HuggingFaceIndusAdapter(BaseAdapter):
    source_id = "hf_indus_decipher"

    def fetch(self) -> list[HistoricalRecord]:
        # Prefer datasets library if installed; otherwise record limitation.
        try:
            from datasets import load_dataset  # type: ignore
        except ImportError:
            self.mark_status(
                DownloadStatus.API_LIMITED,
                "Install `datasets` and confirm licence before loading joyboseroy/indus_decipher",
            )
            return []

        try:
            ds = load_dataset("joyboseroy/indus_decipher", split="train")
            records: list[HistoricalRecord] = []
            for i, row in enumerate(ds):
                if i >= 200:
                    break
                seq = row.get("signs") or row.get("sign_sequence") or row.get("text")
                if isinstance(seq, str):
                    signs = seq.split()
                elif isinstance(seq, list):
                    signs = [str(s) for s in seq]
                else:
                    continue
                rid = str(row.get("id") or row.get("inscription_id") or f"hf_indus_{i}")
                records.append(
                    HistoricalRecord(
                        record_id=f"HF-INDUS-{rid}",
                        civilisation="indus",
                        language=None,
                        writing_system="indus_script",
                        sign_sequence=signs,
                        archaeological_site=row.get("site"),
                        object_type=row.get("object_type"),
                        source_reference="huggingface:joyboseroy/indus_decipher",
                        translation=None,
                        translation_status="none",
                        is_synthetic=False,
                        metadata={"hf_row_index": i, "raw_keys": list(row.keys())},
                    )
                )
            self.mark_status(
                DownloadStatus.AVAILABLE if records else DownloadStatus.PARTIAL,
                f"Loaded {len(records)} rows (capped)",
            )
            return records
        except Exception as exc:  # noqa: BLE001
            self.mark_status(DownloadStatus.FAILED, str(exc))
            return []


class SyntheticIndusAdapter(BaseAdapter):
    source_id = "synthetic_test_corpora"

    def fetch(self) -> list[HistoricalRecord]:
        path = SYNTHETIC_DIR / "corpora.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return [HistoricalRecord.from_dict(r) for r in data.get("indus", [])]
        return build_synthetic_corpora()["indus"]
