"""Transliteration convention helpers.

Converts known convention markers into a lightweight common form for comparison.
Does not invent phonetic values for Indus signs.
"""

from __future__ import annotations

import re
from typing import Callable

CONVENTIONS: dict[str, Callable[[str], str]] = {}


def _identity(text: str) -> str:
    return text.strip()


def sumerian_ascii(text: str) -> str:
    """Light normalisation of ASCII Sumerological transliteration."""
    t = text.strip().lower()
    t = t.replace("š", "sz").replace("ŋ", "j").replace("ḫ", "h")
    t = re.sub(r"\s+", " ", t)
    return t


def akkadian_ascii(text: str) -> str:
    t = text.strip().lower()
    t = t.replace("ṣ", "s,").replace("ṭ", "t,").replace("š", "sz")
    t = re.sub(r"\s+", " ", t)
    return t


def egyptian_trilit(text: str) -> str:
    t = text.strip().lower()
    t = t.replace("ꜣ", "A").replace("ꜥ", "a").replace("ḥ", "H").replace("ḫ", "x")
    t = re.sub(r"\s+", " ", t)
    return t


def indus_passthrough(text: str) -> str:
    """Indus has no established phonetic transliteration — preserve tokens."""
    return text.strip()


CONVENTIONS.update(
    {
        "sumerian_ascii": sumerian_ascii,
        "akkadian_ascii": akkadian_ascii,
        "egyptian_trilit": egyptian_trilit,
        "indus_passthrough": indus_passthrough,
        "identity": _identity,
    }
)


def convert(text: str, convention: str = "identity") -> str:
    fn = CONVENTIONS.get(convention, _identity)
    return fn(text)
