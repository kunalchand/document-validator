import re
import json
from typing import List, Optional

from app.agents.schemas import DocumentSegment, RuleCandidate
from app.core import get_logger

logger = get_logger(__name__)

RULE_EXTRACTION_PROMPT = """You are a compliance document analyst. Extract all compliance rules and requirements from the following document section.

Document section:
{content}

For each rule or requirement you identify, extract:
- title: A brief, descriptive title (max 10 words)
- description: Full description of the requirement
- conditions: List of specific conditions or criteria that must be met
- expected_evidence: List of documents, artifacts, or actions that prove compliance
- severity: "high" (legal/critical obligations), "medium" (important requirements), or "low" (recommendations)
- section: Section heading or reference if visible in the text (null if not applicable)

Return ONLY a valid JSON array. If no rules are found in this section, return an empty array [].

Format:
[
  {{
    "title": "...",
    "description": "...",
    "conditions": ["...", "..."],
    "expected_evidence": ["...", "..."],
    "severity": "high|medium|low",
    "section": "..." or null
  }}
]"""

_VALID_SEVERITIES = {"high", "medium", "low"}


def segment_text(text: str, max_chars: int = 3000) -> List[DocumentSegment]:
    """Split document text into logical segments by section headings or chunk size"""
    lines = text.split("\n")
    section_starts = [0]

    for i, line in enumerate(lines):
        if i > 0 and _is_section_heading(line.strip()):
            section_starts.append(i)

    segments: List[DocumentSegment] = []
    boundaries = section_starts + [len(lines)]

    for j in range(len(section_starts)):
        block = "\n".join(lines[boundaries[j]:boundaries[j + 1]]).strip()
        if not block:
            continue

        if len(block) > max_chars:
            for chunk in _chunk_text(block, max_chars):
                segments.append(DocumentSegment(
                    index=len(segments),
                    title=_infer_title(chunk),
                    content=chunk,
                    char_count=len(chunk),
                ))
        else:
            segments.append(DocumentSegment(
                index=len(segments),
                title=_infer_title(block),
                content=block,
                char_count=len(block),
            ))

    if not segments:
        for i, chunk in enumerate(_chunk_text(text, max_chars)):
            segments.append(DocumentSegment(
                index=i,
                title=f"Section {i + 1}",
                content=chunk,
                char_count=len(chunk),
            ))

    logger.info(f"Segmented document into {len(segments)} sections")
    return segments


def _is_section_heading(line: str) -> bool:
    if not line or len(line) > 120:
        return False

    if re.match(r"^\d+[\.\)]\s+\w", line):
        return True

    if line.isupper() and len(line) >= 4:
        return True

    if line.startswith("#"):
        return True

    if re.match(r"^(?:Section|Article|Part|Chapter)\s+\w", line, re.IGNORECASE):
        return True

    return False


def _chunk_text(text: str, max_chars: int) -> List[str]:
    """Split text into chunks at paragraph boundaries"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append("\n\n".join(current))

    return chunks or [text[:max_chars]]


def _infer_title(content: str) -> Optional[str]:
    first_line = content.split("\n")[0].strip()
    if first_line and len(first_line) <= 80:
        return first_line
    return None


def build_extraction_prompt(segment: DocumentSegment) -> str:
    """Build the LLM prompt for rule extraction from a segment"""
    return RULE_EXTRACTION_PROMPT.format(content=segment.content)


def parse_llm_response(content: str, segment_index: int) -> List[RuleCandidate]:
    """Parse LLM JSON response into RuleCandidate objects"""
    try:
        json_str = _extract_json_array(content)
        if not json_str:
            logger.warning(f"No JSON array in LLM response for segment {segment_index}")
            return []

        raw_rules = json.loads(json_str)
        if not isinstance(raw_rules, list):
            logger.warning(f"LLM response is not a list for segment {segment_index}")
            return []

        candidates: List[RuleCandidate] = []
        for item in raw_rules:
            if not isinstance(item, dict):
                continue
            try:
                severity = str(item.get("severity", "medium")).lower()
                if severity not in _VALID_SEVERITIES:
                    severity = "medium"

                candidate = RuleCandidate(
                    title=str(item.get("title", "Unnamed Rule")),
                    description=str(item.get("description", "")),
                    conditions=[str(c) for c in item.get("conditions", []) if c],
                    expected_evidence=[str(e) for e in item.get("expected_evidence", []) if e],
                    severity=severity,
                    section=item.get("section") or None,
                    source_segment_index=segment_index,
                )
                candidates.append(candidate)
            except Exception as e:
                logger.warning(f"Skipping malformed rule candidate: {e}")

        return candidates

    except json.JSONDecodeError as e:
        snippet = content[:300].replace("\n", " ") if content else ""
        logger.warning(
            f"JSON decode error for segment {segment_index}: {e} | "
            f"LLM response (first 300 chars): {snippet!r}"
        )
        return []
    except Exception as e:
        logger.exception(f"Unexpected error parsing LLM response for segment {segment_index}")
        return []


def _extract_json_array(content: str) -> Optional[str]:
    """Extract a JSON array from text, stripping markdown code fences if present"""
    content = content.strip()

    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            content = content[start:end].strip()
    elif "```" in content:
        start = content.find("```") + 3
        end = content.find("```", start)
        if end > start:
            content = content[start:end].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        return content[start:end + 1]

    return None


def deduplicate_rules(candidates: List[RuleCandidate]) -> List[RuleCandidate]:
    """Remove duplicate rule candidates based on normalized title"""
    seen: set[str] = set()
    unique: List[RuleCandidate] = []

    for candidate in candidates:
        key = candidate.title.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
        else:
            logger.debug(f"Deduplicating rule: '{candidate.title}'")

    return unique
