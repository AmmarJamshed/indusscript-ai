"""Helpers for indexing historical trade / contact evidence fields."""

from __future__ import annotations

import re
from typing import Iterable

# Keyword patterns used to flag relevant passages in ingested texts.
MELUHHA_PATTERNS = [
    re.compile(r"me-?luh-?ha", re.I),
    re.compile(r"meluhha", re.I),
    re.compile(r"meluḫḫa", re.I),
]
INTERPRETER_PATTERNS = [
    re.compile(r"eme-bal", re.I),
    re.compile(r"targumannu", re.I),
    re.compile(r"interpreter", re.I),
]
TRADE_PATTERNS = [
    re.compile(r"dilmun", re.I),
    re.compile(r"magan", re.I),
    re.compile(r"copper", re.I),
    re.compile(r"carnelian", re.I),
    re.compile(r"merchant", re.I),
]


def flag_text(text: str) -> dict:
    return {
        "mentions_meluhha": any(p.search(text) for p in MELUHHA_PATTERNS),
        "mentions_interpreter": any(p.search(text) for p in INTERPRETER_PATTERNS),
        "mentions_trade_keywords": any(p.search(text) for p in TRADE_PATTERNS),
    }


def extract_from_translations(texts: Iterable[str]) -> list[dict]:
    out = []
    for i, text in enumerate(texts):
        flags = flag_text(text)
        if any(flags.values()):
            out.append({"index": i, "text": text, **flags})
    return out
