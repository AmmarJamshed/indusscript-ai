"""Exportable research reports (JSON / CSV / Markdown)."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from analysis.sequence_analysis import compare_corpora
from config.settings import INTEGRITY_NOTICE, REPORTS_DIR, RESEARCH_QUESTIONS, ensure_directories
from corpora.loader import load_sequences
from database.db import get_db
from historical.meluhha import meluhha_summary
from historical.trade_network import graph_summary
from hypotheses.candidate_languages import score_hypotheses
from hypotheses.falsification import run_falsification_suite
from hypotheses.inference import interpretation_report


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _jsonable(obj):
    """Recursively convert tuples/sets for JSON export."""
    if isinstance(obj, dict):
        return {str(k) if not isinstance(k, (str, int, float, bool, type(None))) else k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, set):
        return [_jsonable(x) for x in obj]
    if isinstance(obj, Path):
        return str(obj)
    return obj


def build_full_report(n_perm: int = 200) -> dict:
    db = get_db()
    civs = list(db.count_by_civilisation().keys())
    corpora = {c: load_sequences(c, db) for c in civs if c != "proto_dravidian"}
    corpora = {k: v for k, v in corpora.items() if v}
    structural = compare_corpora(corpora) if corpora else {}
    indus = corpora.get("indus", [])
    comparison = corpora.get("sumerian") or corpora.get("akkadian") or corpora.get("egyptian") or []
    falsification = (
        run_falsification_suite(indus, comparison, n_perm=n_perm)
        if indus and comparison
        else {"note": "Insufficient corpora for falsification"}
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "integrity_notice": INTEGRITY_NOTICE,
        "research_questions": RESEARCH_QUESTIONS,
        "corpus_counts": db.count_by_civilisation(),
        "sources": db.list_sources(),
        "structural_comparison": structural,
        "meluhha": meluhha_summary(db),
        "trade_network": graph_summary(),
        "language_hypotheses": [h.to_dict() for h in score_hypotheses()],
        "candidate_interpretations": interpretation_report(db),
        "falsification": falsification,
        "disclaimer": (
            "This report does not constitute a decipherment of the Indus script."
        ),
    }


def export_report(n_perm: int = 200) -> dict[str, Path]:
    ensure_directories()
    report = build_full_report(n_perm=n_perm)
    stamp = _stamp()
    json_path = REPORTS_DIR / f"research_report_{stamp}.json"
    md_path = REPORTS_DIR / f"research_report_{stamp}.md"
    csv_path = REPORTS_DIR / f"corpus_counts_{stamp}.csv"

    json_path.write_text(
        json.dumps(_jsonable(report), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# IndusScript AI Research Report",
        "",
        INTEGRITY_NOTICE,
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Research questions",
    ]
    for k, v in RESEARCH_QUESTIONS.items():
        lines.append(f"- **{k}**: {v}")
    lines += ["", "## Corpus counts"]
    for civ, n in report["corpus_counts"].items():
        lines.append(f"- {civ}: {n}")
    lines += [
        "",
        "## Disclaimer",
        report["disclaimer"],
        "",
        "Full machine-readable output is in the companion JSON file.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["civilisation", "n_records"])
        for civ, n in report["corpus_counts"].items():
            writer.writerow([civ, n])

    return {"json": json_path, "markdown": md_path, "csv": csv_path}
