from datetime import datetime, timezone
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse

class EvidenceItem(BaseModel):
    """Standardized evidence record produced by tools or LLM inference.

    - ``source_type`` enumerates the provenance of the evidence.
    - ``confidence`` is a percentile (0‑100) reflecting trustworthiness.
    - ``timestamp`` is timezone-aware UTC ISO string.
    """
    finding: str = Field(..., description="Brief description of the finding or claim")
    source: str = Field(..., description="Human readable source name, e.g. 'Firecrawl', 'Google Search'")
    source_type: Literal["website", "search", "api", "database", "llm", "assumption", "unavailable"] = Field(
        ..., description="Category of source provenance"
    )
    url: Optional[str] = Field(
        None, description="URL of the source when applicable"
    )
    evidence: Optional[Any] = Field(
        None, description="Raw evidence payload (JSON, text snippet, etc.)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=100.0, description="Confidence score on a 0‑100 scale"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="UTC timestamp"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        # Basic sanity check for valid URL format
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            # If missing scheme, prepend https:// if it looks like a domain
            if "." in v and not v.startswith("http"):
                v = "https://" + v
                parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: '{v}'")
        return str(v)

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if v < 0.0 or v > 100.0:
            raise ValueError("Confidence must be between 0.0 and 100.0")
        return round(float(v), 2)

    @classmethod
    def from_tool_result(
        cls,
        finding: str,
        source: str,
        source_type: str,
        url: Optional[str] = None,
        evidence: Optional[Any] = None,
        confidence: float = 100.0,
    ) -> "EvidenceItem":
        """Factory helper used by BaseAgent when a tool succeeds or fails."""
        return cls(
            finding=finding,
            source=source,
            source_type=source_type,  # type: ignore[arg-type]
            url=url,
            evidence=evidence,
            confidence=confidence,
        )
