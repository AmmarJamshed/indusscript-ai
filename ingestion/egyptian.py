"""Ancient Egyptian source adapters."""

from __future__ import annotations

from config.logging_config import setup_logging
from database.models import DownloadStatus, HistoricalRecord
from ingestion.base import BaseAdapter
from ingestion.synthetic import build_synthetic_corpora

logger = setup_logging("ingestion.egyptian")


class TLAAdapter(BaseAdapter):
    source_id = "tla"

    def fetch(self) -> list[HistoricalRecord]:
        try:
            resp = self.http_get("https://tla.digital/")
            self.save_raw(
                "tla_probe.json",
                {"status_code": resp.status_code, "bytes": len(resp.content)},
            )
            self.mark_status(
                DownloadStatus.API_LIMITED,
                "TLA reachable. Use documented API/licence before ingesting lemmas.",
            )
        except Exception as exc:  # noqa: BLE001
            self.mark_status(DownloadStatus.UNAVAILABLE, str(exc))
        return []


class HuggingFaceEgyptianAdapter(BaseAdapter):
    source_id = "hf_bbaw_egyptian"

    def fetch(self) -> list[HistoricalRecord]:
        try:
            from datasets import load_dataset  # type: ignore
        except ImportError:
            self.mark_status(
                DownloadStatus.API_LIMITED,
                "Install `datasets` and verify licence for phiwi/bbaw_egyptian",
            )
            return []
        try:
            ds = load_dataset("phiwi/bbaw_egyptian", split="train")
            records: list[HistoricalRecord] = []
            for i, row in enumerate(ds):
                if i >= 100:
                    break
                text = row.get("text") or row.get("transliteration") or ""
                signs = str(text).split()
                if not signs:
                    continue
                records.append(
                    HistoricalRecord(
                        record_id=f"HF-EGY-{i}",
                        civilisation="egyptian",
                        language="Ancient Egyptian",
                        writing_system="egyptian_hieroglyphic",
                        transliteration=str(text),
                        translation=row.get("translation"),
                        sign_sequence=signs,
                        source_reference="huggingface:phiwi/bbaw_egyptian",
                        translation_status="attested"
                        if row.get("translation")
                        else "none",
                        is_synthetic=False,
                        metadata={"hf_row_index": i},
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


class SyntheticEgyptianAdapter(BaseAdapter):
    source_id = "synthetic_test_corpora"

    def fetch(self) -> list[HistoricalRecord]:
        return build_synthetic_corpora()["egyptian"]
