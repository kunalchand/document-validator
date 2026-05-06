from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractionEventType(str, Enum):
    parsing_started = "parsing_started"
    parsing_complete = "parsing_complete"
    segmentation_started = "segmentation_started"
    segmentation_complete = "segmentation_complete"
    extraction_started = "extraction_started"
    extraction_progress = "extraction_progress"
    extraction_complete = "extraction_complete"
    finalization_started = "finalization_started"
    finalization_complete = "finalization_complete"
    error = "error"


class ExtractionStage(str, Enum):
    parsing = "parsing"
    segmentation = "segmentation"
    extraction = "extraction"
    finalization = "finalization"


class ExtractionProgress(BaseModel):
    """Positional progress for iterative operations (e.g. per-segment extraction)"""
    current: Optional[int] = Field(default=None, description="Current item index")
    total: Optional[int] = Field(default=None, description="Total items")
    percent: Optional[int] = Field(default=None, description="Completion percentage 0-100")


class ExtractionEventData(BaseModel):
    """Contextual data payload attached to specific event types"""
    # Parsing
    char_count: Optional[int] = None
    page_count: Optional[int] = None

    # Segmentation
    section_count: Optional[int] = None
    section_titles: Optional[List[str]] = None

    # Per-segment extraction
    segment_index: Optional[int] = None
    segment_title: Optional[str] = None
    rules_in_segment: Optional[int] = None
    total_rules_so_far: Optional[int] = None

    # Finalization
    total_rules: Optional[int] = None
    unique_rules: Optional[int] = None
    extracted_rules: Optional[List[dict]] = Field(
        default=None,
        description="Full extracted rules list — only present in finalization_complete event"
    )


class ExtractionEvent(BaseModel):
    """
    A single event emitted by the Phase 1 extraction pipeline.
    This schema is shared between backend (Python) and frontend (TypeScript).
    """
    event_type: ExtractionEventType
    stage: ExtractionStage
    message: str = Field(..., description="Human-readable status message")
    progress: Optional[ExtractionProgress] = None
    data: Optional[ExtractionEventData] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp"
    )
    event_id: Optional[str] = Field(
        default=None,
        description="SSE event ID for Last-Event-ID resumption tracking"
    )
