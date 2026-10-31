"""Central configuration for IndusScript AI."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
LOG_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
DB_PATH = DATA_DIR / "indusscript.db"

# Research integrity banner shown in UI and reports
INTEGRITY_NOTICE = (
    "IndusScript AI does not claim that the Indus script has been deciphered. "
    "Similarity scores, embeddings and candidate readings are hypotheses for "
    "scientific evaluation — not established translations or proof of linguistic ancestry."
)

# Four research questions — never conflate these
RESEARCH_QUESTIONS = {
    "A": "Are the symbols visually similar?",
    "B": "Do the writing systems exhibit similar structural properties?",
    "C": "Is there evidence of linguistic relationships, borrowing or contact?",
    "D": "Can any Indus sign sequences be assigned defensible candidate meanings?",
}

DEFAULT_NGRAM_ORDERS = (1, 2, 3, 4)
DEFAULT_FALSIFICATION_PERMUTATIONS = 1000
DEFAULT_BOOTSTRAP_SAMPLES = 500
CACHE_TTL_SECONDS = 3600
HTTP_TIMEOUT = 30
HTTP_RETRIES = 3
USER_AGENT = "IndusScriptAI/0.1 (research; respectful-crawler)"

CIVILISATIONS = (
    "indus",
    "sumerian",
    "akkadian",
    "babylonian",
    "egyptian",
    "proto_dravidian",
    "munda",
    "linear_b",
    "other",
)

WRITING_SYSTEMS = (
    "indus_script",
    "cuneiform",
    "egyptian_hieroglyphic",
    "egyptian_hieratic",
    "egyptian_demotic",
    "linear_b",
    "reconstructed_lexicon",
    "unknown",
)


def ensure_directories() -> None:
    """Create required runtime directories if missing."""
    for path in (
        RAW_DIR,
        PROCESSED_DIR,
        EXTERNAL_DIR,
        SYNTHETIC_DIR,
        LOG_DIR,
        REPORTS_DIR,
        DATA_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
