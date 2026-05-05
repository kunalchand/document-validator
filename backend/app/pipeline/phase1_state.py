from typing import TypedDict, List, Optional, Annotated
import operator

from app.agents.schemas import DocumentSegment, RuleCandidate


class Phase1State(TypedDict):
    """LangGraph state flowing through the Phase 1 rules extraction pipeline"""

    # --- Input ---
    input_type: str          # "pdf" | "docx" | "text"
    raw_file_bytes: Optional[bytes]
    raw_filename: Optional[str]
    raw_text: Optional[str]

    # --- After parse_input node ---
    parsed_text: Optional[str]

    # --- After segment_content node ---
    segments: List[DocumentSegment]

    # --- After orchestrate_extraction node ---
    rule_candidates: List[RuleCandidate]

    # --- After finalize_rules node ---
    extracted_rules: List[dict]   # serialisable Rule dicts

    # --- Accumulated warnings (non-fatal) ---
    errors: Annotated[List[str], operator.add]
