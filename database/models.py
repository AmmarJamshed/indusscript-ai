"""Unified historical data model.

Original source payloads are stored separately from normalised records.
Indus inscriptions must never carry invented translations as facts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EvidenceTier(str, Enum):
    """Epistemic status of a claim."""

    OBSERVED_FACT = "observed_fact"
    COMPUTATIONAL_OBSERVATION = "computational_observation"
    LINGUISTIC_HYPOTHESIS = "linguistic_hypothesis"
    SPECULATIVE_INTERPRETATION = "speculative_interpretation"
    INDEPENDENTLY_VALIDATED = "independently_validated"


class DownloadStatus(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    AVAILABLE = "available"
    PARTIAL = "partial"
    BLOCKED_BY_LICENCE = "blocked_by_licence"
    UNAVAILABLE = "unavailable"
    API_LIMITED = "api_limited"
    SYNTHETIC_ONLY = "synthetic_only"
    FAILED = "failed"


@dataclass
class UncertaintyAnnotation:
    field_name: str
    reason: str
    confidence: float = 0.0


@dataclass
class HistoricalRecord:
    """Normalised inscription / text record."""

    record_id: str
    civilisation: str
    language: str | None
    writing_system: str
    original_script: str | None = None
    transliteration: str | None = None
    translation: str | None = None  # Must be None for undeciphered Indus unless labelled
    sign_sequence: list[str] = field(default_factory=list)
    sign_inventory: list[str] = field(default_factory=list)
    reading_direction: str | None = None  # LTR, RTL, UNKNOWN, BIDIRECTIONAL
    date_range: str | None = None
    geographical_location: str | None = None
    archaeological_site: str | None = None
    object_type: str | None = None
    source_reference: str | None = None
    image_reference: str | None = None
    confidence: float = 1.0
    uncertainty_annotations: list[UncertaintyAnnotation] = field(default_factory=list)
    is_synthetic: bool = False
    translation_status: str = "none"  # none | attested | hypothesis | synthetic
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["uncertainty_annotations"] = [
            asdict(u) if isinstance(u, UncertaintyAnnotation) else u
            for u in self.uncertainty_annotations
        ]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HistoricalRecord:
        anns = [
            UncertaintyAnnotation(**a) if isinstance(a, dict) else a
            for a in data.get("uncertainty_annotations", [])
        ]
        payload = dict(data)
        payload["uncertainty_annotations"] = anns
        payload.setdefault("sign_sequence", [])
        payload.setdefault("sign_inventory", [])
        payload.setdefault("metadata", {})
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in payload.items() if k in known}
        return cls(**filtered)


@dataclass
class RawSourcePayload:
    """Preserved original source blob, separate from normalised data."""

    payload_id: str
    source_id: str
    original_identifier: str
    retrieved_at: str
    content_type: str
    raw_json: dict[str, Any]
    licence_note: str | None = None


@dataclass
class SourceRegistryEntry:
    source_id: str
    name: str
    url: str
    civilisation: str
    format: str
    licence: str
    redistribution_ok: bool
    api_limitations: str
    availability: str
    download_status: DownloadStatus
    data_quality: str
    notes: str = ""
    last_checked: str | None = None


@dataclass
class MeluhhaEvidence:
    evidence_id: str
    original_text: str | None
    transliteration: str | None
    translation: str | None
    date: str | None
    source_citation: str
    historical_location: str | None
    named_people: list[str] = field(default_factory=list)
    commodity_references: list[str] = field(default_factory=list)
    confidence: float = 0.5
    uncertainty: str = ""
    period: str | None = None
    mentions_interpreter: bool = False
    is_synthetic: bool = False
    evidence_tier: EvidenceTier = EvidenceTier.LINGUISTIC_HYPOTHESIS

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_tier"] = self.evidence_tier.value
        return data


@dataclass
class CandidateInterpretation:
    """A proposed reading — always a hypothesis unless validated."""

    interpretation_id: str
    inscription_id: str
    sign_sequence: list[str]
    archaeological_context: str | None
    proposed_structure: str | None
    candidate_language: str
    reconstructed_vocabulary: list[str]
    correspondence_explanation: str
    alternative_explanations: list[str]
    held_out_test_result: str | None
    contradictions: list[str]
    confidence: float
    evidence_tier: EvidenceTier = EvidenceTier.SPECULATIVE_INTERPRETATION
    assumptions: list[str] = field(default_factory=list)
    is_synthetic: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_tier"] = self.evidence_tier.value
        return data


@dataclass
class HypothesisScore:
    hypothesis_id: str
    label: str
    scores: dict[str, float]
    overall: float
    notes: list[str]
    evidence_tier: EvidenceTier = EvidenceTier.LINGUISTIC_HYPOTHESIS

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_tier"] = self.evidence_tier.value
        return data
