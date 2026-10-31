"""Mesopotamian source adapters (CDLI / ORACC / NaBuCCo / etc.).

Respect Terms of Service. Probe connectivity and document status; do not scrape
restricted content or fabricate tablets.
"""

from __future__ import annotations

from config.logging_config import setup_logging
from database.models import DownloadStatus, HistoricalRecord
from ingestion.base import BaseAdapter
from ingestion.synthetic import build_synthetic_corpora

logger = setup_logging("ingestion.mesopotamia")


class CDLIAdapter(BaseAdapter):
    source_id = "cdli"

    def fetch(self) -> list[HistoricalRecord]:
        try:
            resp = self.http_get("https://cdli.earth/")
            self.save_raw(
                "cdli_home_probe.json",
                {"status_code": resp.status_code, "bytes": len(resp.content)},
            )
            self.mark_status(
                DownloadStatus.API_LIMITED,
                "CDLI reachable. Use authorised catalogue exports / documented APIs; "
                "bulk scrape not performed.",
            )
        except Exception as exc:  # noqa: BLE001
            self.mark_status(DownloadStatus.UNAVAILABLE, str(exc))
        return []


class ORACCAdapter(BaseAdapter):
    source_id = "oracc"

    def fetch(self) -> list[HistoricalRecord]:
        try:
            resp = self.http_get("https://oracc.org/")
            self.save_raw(
                "oracc_home_probe.json",
                {"status_code": resp.status_code, "bytes": len(resp.content)},
            )
            self.mark_status(
                DownloadStatus.API_LIMITED,
                "ORACC portal reachable. Import project JSON/ATF selectively with attribution.",
            )
        except Exception as exc:  # noqa: BLE001
            self.mark_status(DownloadStatus.UNAVAILABLE, str(exc))
        return []


class NaBuCCoAdapter(BaseAdapter):
    source_id = "nabucco"

    def fetch(self) -> list[HistoricalRecord]:
        api = "https://nabucco.acdh.oeaw.ac.at/api/"
        try:
            resp = self.http_get(api)
            snippet = resp.text[:2000]
            self.save_raw(
                "nabucco_api_probe.json",
                {"status_code": resp.status_code, "snippet": snippet},
            )
            self.mark_status(
                DownloadStatus.PARTIAL,
                "API endpoint probed. Map concrete resources before bulk import.",
            )
        except Exception as exc:  # noqa: BLE001
            self.mark_status(DownloadStatus.UNAVAILABLE, str(exc))
        return []


class SyntheticMesopotamiaAdapter(BaseAdapter):
    """Loads SYNTHETIC Sumerian/Akkadian test rows only."""

    source_id = "synthetic_test_corpora"

    def fetch(self) -> list[HistoricalRecord]:
        corpora = build_synthetic_corpora()
        return corpora["sumerian"] + corpora["akkadian"]
