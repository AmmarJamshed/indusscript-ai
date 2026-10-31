"""Base ingestion adapter with caching, retries and provenance logging."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config.logging_config import setup_logging
from config.settings import HTTP_RETRIES, HTTP_TIMEOUT, RAW_DIR, USER_AGENT
from database.db import Database
from database.models import DownloadStatus, HistoricalRecord
from ingestion.source_registry import update_download_status

logger = setup_logging("ingestion")


class BaseAdapter(ABC):
    source_id: str = "base"

    def __init__(self, db: Database) -> None:
        self.db = db
        self.raw_dir = RAW_DIR / self.source_id
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    @retry(
        stop=stop_after_attempt(HTTP_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def http_get(self, url: str) -> requests.Response:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        return resp

    def save_raw(self, name: str, payload: dict[str, Any]) -> Path:
        path = self.raw_dir / name
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def mark_status(self, status: DownloadStatus, notes: str | None = None) -> None:
        update_download_status(self.db, self.source_id, status, notes)
        logger.info("%s -> %s (%s)", self.source_id, status.value, notes or "")

    @abstractmethod
    def fetch(self) -> list[HistoricalRecord]:
        """Attempt retrieval. Must not fabricate historical records."""

    def run(self) -> list[HistoricalRecord]:
        try:
            records = self.fetch()
            for rec in records:
                self.db.upsert_record(rec)
                self.db.store_raw_payload(
                    payload_id=f"raw_{rec.record_id}",
                    source_id=self.source_id,
                    original_identifier=rec.record_id,
                    content_type="application/json",
                    raw_json=rec.to_dict(),
                    licence_note="See source registry",
                )
            if records:
                self.mark_status(
                    DownloadStatus.AVAILABLE
                    if not all(r.is_synthetic for r in records)
                    else DownloadStatus.SYNTHETIC_ONLY,
                    f"ingested {len(records)} records",
                )
            return records
        except Exception as exc:  # noqa: BLE001 — adapters must survive failures
            logger.exception("Adapter %s failed: %s", self.source_id, exc)
            self.mark_status(DownloadStatus.FAILED, str(exc))
            return []
