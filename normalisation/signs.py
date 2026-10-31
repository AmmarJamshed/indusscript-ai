"""Sign normalisation engine.

Canonicalises identifiers within a civilisation. Does NOT equate visually
similar signs across civilisations without explicit evidence.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from config.settings import PROCESSED_DIR, ensure_directories


DAMAGED_TOKEN = "[DAMAGED]"
UNCERTAIN_PREFIX = "?"
CROSS_CIV_EQUIVALENCE_FORBIDDEN = True


@dataclass
class SignMapping:
    civilisation: str
    raw_id: str
    canonical_id: str
    damaged: bool = False
    uncertain: bool = False
    image_path: str | None = None
    notes: str = ""


@dataclass
class SignVocabulary:
    civilisation: str
    signs: dict[str, SignMapping] = field(default_factory=dict)

    def add(self, mapping: SignMapping) -> None:
        self.signs[mapping.raw_id] = mapping

    def canonicalise(self, raw: str) -> str:
        if raw in self.signs:
            m = self.signs[raw]
            if m.damaged:
                return DAMAGED_TOKEN
            if m.uncertain:
                return f"{UNCERTAIN_PREFIX}{m.canonical_id}"
            return m.canonical_id
        return normalise_token(raw)

    def to_dict(self) -> dict:
        return {
            "civilisation": self.civilisation,
            "signs": {k: v.__dict__ for k, v in self.signs.items()},
        }


def normalise_token(token: str) -> str:
    """Normalise a single sign token without inventing cross-script merges."""
    t = token.strip()
    if not t:
        return DAMAGED_TOKEN
    if t in {"#", "...", "[...]", "x", "X", "†"}:
        return DAMAGED_TOKEN
    uncertain = t.startswith("?") or t.endswith("?")
    t = t.strip("?")
    t = re.sub(r"\s+", "", t)
    t = t.upper()
    # Collapse common separator variants within the same token family
    t = t.replace("–", "-").replace("—", "-")
    if uncertain:
        return f"{UNCERTAIN_PREFIX}{t}"
    return t


def reverse_sequence(seq: list[str]) -> list[str]:
    return list(reversed(seq))


def normalise_sequence(
    sequence: list[str],
    vocabulary: SignVocabulary | None = None,
    reading_direction: str | None = None,
    force_reverse: bool = False,
) -> list[str]:
    out = []
    for tok in sequence:
        if vocabulary:
            out.append(vocabulary.canonicalise(str(tok)))
        else:
            out.append(normalise_token(str(tok)))
    if force_reverse or (reading_direction or "").upper() == "FORCE_REVERSE":
        out = reverse_sequence(out)
    return out


class MappingRegistry:
    """Per-civilisation sign maps. Cross-civ links require explicit evidence flag."""

    def __init__(self) -> None:
        self.vocabularies: dict[str, SignVocabulary] = {}
        self.cross_civilisation_links: list[dict] = []

    def vocabulary(self, civilisation: str) -> SignVocabulary:
        if civilisation not in self.vocabularies:
            self.vocabularies[civilisation] = SignVocabulary(civilisation=civilisation)
        return self.vocabularies[civilisation]

    def register_alias(
        self,
        civilisation: str,
        raw_id: str,
        canonical_id: str,
        *,
        damaged: bool = False,
        uncertain: bool = False,
        image_path: str | None = None,
        notes: str = "",
    ) -> None:
        self.vocabulary(civilisation).add(
            SignMapping(
                civilisation=civilisation,
                raw_id=raw_id,
                canonical_id=canonical_id,
                damaged=damaged,
                uncertain=uncertain,
                image_path=image_path,
                notes=notes,
            )
        )

    def propose_cross_link(
        self,
        civ_a: str,
        sign_a: str,
        civ_b: str,
        sign_b: str,
        evidence: str,
        approved: bool = False,
    ) -> None:
        if not approved:
            raise ValueError(
                "Cross-civilisation sign equivalence requires explicit evidence "
                "and approved=True. Visual similarity alone is insufficient."
            )
        self.cross_civilisation_links.append(
            {
                "civ_a": civ_a,
                "sign_a": sign_a,
                "civ_b": civ_b,
                "sign_b": sign_b,
                "evidence": evidence,
                "approved": True,
            }
        )

    def save(self, path: Path | None = None) -> Path:
        ensure_directories()
        path = path or (PROCESSED_DIR / "sign_mapping_registry.json")
        payload = {
            "vocabularies": {k: v.to_dict() for k, v in self.vocabularies.items()},
            "cross_civilisation_links": self.cross_civilisation_links,
            "policy": {
                "cross_civ_equivalence_without_evidence": False,
                "damaged_token": DAMAGED_TOKEN,
            },
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


def build_default_registry_from_sequences(
    civilisation: str, sequences: list[list[str]]
) -> SignVocabulary:
    vocab = SignVocabulary(civilisation=civilisation)
    seen: set[str] = set()
    for seq in sequences:
        for tok in seq:
            raw = str(tok)
            canon = normalise_token(raw)
            if raw in seen:
                continue
            seen.add(raw)
            vocab.add(
                SignMapping(
                    civilisation=civilisation,
                    raw_id=raw,
                    canonical_id=canon.lstrip("?"),
                    uncertain=canon.startswith("?"),
                    damaged=canon == DAMAGED_TOKEN,
                )
            )
    return vocab
