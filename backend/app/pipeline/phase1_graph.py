import asyncio
from typing import Optional
from functools import lru_cache

from langgraph.graph import StateGraph, END, START

from app.pipeline.phase1_state import Phase1State
from app.parsers import PDFParser, DOCXParser, TextParser
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest
from app.agents.schemas import DocumentSegment, RuleCandidate
from app.agents.nodes import (
    segment_text,
    build_extraction_prompt,
    parse_llm_response,
    deduplicate_rules,
)
from app.core import get_logger
from app.core.exceptions import FileParseFailed, ExtractionFailed

logger = get_logger(__name__)


class Phase1Pipeline:
    """
    LangGraph pipeline for Phase 1: rules extraction.

    Flow: parse_input → segment_content → orchestrate_extraction → finalize_rules
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider
        self._pdf_parser = PDFParser()
        self._docx_parser = DOCXParser()
        self._text_parser = TextParser()
        self._graph = self._build_graph()

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self):
        graph = StateGraph(Phase1State)

        graph.add_node("parse_input", self._parse_input)
        graph.add_node("segment_content", self._segment_content)
        graph.add_node("orchestrate_extraction", self._orchestrate_extraction)
        graph.add_node("finalize_rules", self._finalize_rules)

        graph.add_edge(START, "parse_input")
        graph.add_edge("parse_input", "segment_content")
        graph.add_edge("segment_content", "orchestrate_extraction")
        graph.add_edge("orchestrate_extraction", "finalize_rules")
        graph.add_edge("finalize_rules", END)

        return graph.compile()

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _parse_input(self, state: Phase1State) -> dict:
        """Route input to the appropriate parser and return plain text"""
        input_type = state["input_type"]
        logger.info(f"Parsing input: type={input_type}")

        try:
            if input_type == "pdf":
                text = self._pdf_parser.parse(state["raw_file_bytes"])
            elif input_type == "docx":
                text = self._docx_parser.parse(state["raw_file_bytes"])
            elif input_type == "text":
                text = self._text_parser.parse(state["raw_text"])
            else:
                raise ExtractionFailed(f"Unsupported input type: {input_type}")

            if not text.strip():
                return {"errors": ["Parsed document produced no text"]}

            logger.info(f"Document parsed successfully: {len(text)} chars")
            return {"parsed_text": text}

        except (FileParseFailed, ExtractionFailed):
            raise
        except Exception as e:
            logger.error(f"Unexpected parse error: {e}")
            raise FileParseFailed(str(e), file_type=input_type)

    def _segment_content(self, state: Phase1State) -> dict:
        """Split parsed text into logical segments"""
        parsed_text = state.get("parsed_text") or ""

        if not parsed_text:
            return {"segments": [], "errors": ["No text available for segmentation"]}

        segments = segment_text(parsed_text)
        logger.info(f"Content segmented into {len(segments)} sections")
        return {"segments": segments}

    async def _orchestrate_extraction(self, state: Phase1State) -> dict:
        """Fan-out: parallel LLM extraction per segment. Fan-in: aggregate candidates."""
        segments: list[DocumentSegment] = state.get("segments", [])

        if not segments:
            logger.warning("No segments to process — returning empty candidates")
            return {"rule_candidates": []}

        logger.info(f"Dispatching {len(segments)} segment workers")

        tasks = [self._worker_extract(seg) for seg in segments]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_candidates: list[RuleCandidate] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Worker for segment {i} failed: {result}")
            else:
                all_candidates.extend(result)

        logger.info(f"Orchestration complete: {len(all_candidates)} raw rule candidates")
        return {"rule_candidates": all_candidates}

    async def _worker_extract(self, segment: DocumentSegment) -> list[RuleCandidate]:
        """Worker: call LLM for a single segment and parse the response"""
        try:
            request = LLMRequest(
                prompt=build_extraction_prompt(segment),
                temperature=0.2,
                max_tokens=2000,
                system_prompt=(
                    "You are a compliance document analyst. "
                    "Always respond with valid JSON only."
                ),
            )
            response = await self._llm.generate(request)
            candidates = parse_llm_response(response.content, segment.index)
            logger.debug(f"Segment {segment.index}: {len(candidates)} candidates extracted")
            return candidates
        except Exception as e:
            logger.error(f"Worker failed for segment {segment.index}: {e}")
            raise

    def _finalize_rules(self, state: Phase1State) -> dict:
        """Deduplicate candidates, assign IDs, and serialize to dicts"""
        candidates: list[RuleCandidate] = state.get("rule_candidates", [])
        unique = deduplicate_rules(candidates)

        logger.info(
            f"Finalizing rules: {len(candidates)} candidates → "
            f"{len(unique)} unique rules"
        )

        rules = [
            {
                "id": f"rule_{i + 1:03d}",
                "title": candidate.title,
                "description": candidate.description,
                "conditions": candidate.conditions,
                "expected_evidence": candidate.expected_evidence,
                "section": candidate.section,
                "severity": candidate.severity,
                "status": "extracted",
            }
            for i, candidate in enumerate(unique)
        ]
        return {"extracted_rules": rules}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(
        self,
        input_type: str,
        raw_file_bytes: Optional[bytes] = None,
        raw_filename: Optional[str] = None,
        raw_text: Optional[str] = None,
    ) -> list[dict]:
        """Execute the Phase 1 pipeline and return extracted rules as plain dicts"""
        initial_state: Phase1State = {
            "input_type": input_type,
            "raw_file_bytes": raw_file_bytes,
            "raw_filename": raw_filename,
            "raw_text": raw_text,
            "parsed_text": None,
            "segments": [],
            "rule_candidates": [],
            "extracted_rules": [],
            "errors": [],
        }

        logger.info(f"Phase1Pipeline starting: input_type={input_type}")
        result = await self._graph.ainvoke(initial_state)

        if result.get("errors"):
            logger.warning(f"Pipeline finished with warnings: {result['errors']}")

        rules = result.get("extracted_rules", [])
        logger.info(f"Phase1Pipeline complete: {len(rules)} rules returned")
        return rules
