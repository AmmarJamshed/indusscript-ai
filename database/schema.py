"""SQL schema for SQLite (default) / PostgreSQL-compatible DDL."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    civilisation TEXT,
    format TEXT,
    licence TEXT,
    redistribution_ok INTEGER,
    api_limitations TEXT,
    availability TEXT,
    download_status TEXT,
    data_quality TEXT,
    notes TEXT,
    last_checked TEXT
);

CREATE TABLE IF NOT EXISTS raw_payloads (
    payload_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    original_identifier TEXT,
    retrieved_at TEXT,
    content_type TEXT,
    raw_json TEXT NOT NULL,
    licence_note TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(source_id)
);

CREATE TABLE IF NOT EXISTS records (
    record_id TEXT PRIMARY KEY,
    civilisation TEXT NOT NULL,
    language TEXT,
    writing_system TEXT NOT NULL,
    original_script TEXT,
    transliteration TEXT,
    translation TEXT,
    sign_sequence TEXT NOT NULL,
    sign_inventory TEXT,
    reading_direction TEXT,
    date_range TEXT,
    geographical_location TEXT,
    archaeological_site TEXT,
    object_type TEXT,
    source_reference TEXT,
    image_reference TEXT,
    confidence REAL,
    uncertainty_annotations TEXT,
    is_synthetic INTEGER DEFAULT 0,
    translation_status TEXT DEFAULT 'none',
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS signs (
    sign_id TEXT PRIMARY KEY,
    civilisation TEXT NOT NULL,
    canonical_id TEXT NOT NULL,
    aliases TEXT,
    image_path TEXT,
    damaged INTEGER DEFAULT 0,
    uncertain INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS meluhha_evidence (
    evidence_id TEXT PRIMARY KEY,
    original_text TEXT,
    transliteration TEXT,
    translation TEXT,
    date TEXT,
    source_citation TEXT,
    historical_location TEXT,
    named_people TEXT,
    commodity_references TEXT,
    confidence REAL,
    uncertainty TEXT,
    period TEXT,
    mentions_interpreter INTEGER,
    is_synthetic INTEGER DEFAULT 0,
    evidence_tier TEXT
);

CREATE TABLE IF NOT EXISTS interpretations (
    interpretation_id TEXT PRIMARY KEY,
    inscription_id TEXT,
    sign_sequence TEXT,
    archaeological_context TEXT,
    proposed_structure TEXT,
    candidate_language TEXT,
    reconstructed_vocabulary TEXT,
    correspondence_explanation TEXT,
    alternative_explanations TEXT,
    held_out_test_result TEXT,
    contradictions TEXT,
    confidence REAL,
    evidence_tier TEXT,
    assumptions TEXT,
    is_synthetic INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS analysis_cache (
    cache_key TEXT PRIMARY KEY,
    created_at TEXT,
    payload TEXT
);

CREATE INDEX IF NOT EXISTS idx_records_civ ON records(civilisation);
CREATE INDEX IF NOT EXISTS idx_records_site ON records(archaeological_site);
CREATE INDEX IF NOT EXISTS idx_signs_civ ON signs(civilisation);
"""
