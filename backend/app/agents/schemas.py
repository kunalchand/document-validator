from pydantic import BaseModel, Field
from typing import List, Optional


class DocumentSegment(BaseModel):
    """A logical section of parsed document text"""
    index: int = Field(..., description="Segment index (0-based)")
    title: Optional[str] = Field(default=None, description="Inferred section title")
    content: str = Field(..., description="Segment text content")
    char_count: int = Field(..., description="Character count of segment content")


class RuleCandidate(BaseModel):
    """A rule extracted from a segment before deduplication and finalization"""
    title: str = Field(..., description="Rule title")
    description: str = Field(..., description="Full rule description")
    conditions: List[str] = Field(default_factory=list, description="Specific conditions that must be met")
    expected_evidence: List[str] = Field(default_factory=list, description="Artifacts that prove compliance")
    severity: str = Field(default="medium", description="Severity level: high / medium / low")
    section: Optional[str] = Field(default=None, description="Source section reference")
    source_segment_index: int = Field(default=0, description="Index of originating segment")
