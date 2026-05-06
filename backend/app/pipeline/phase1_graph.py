import asyncio
from typing import AsyncIterator, Optional

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
from app.agents.events import (
    ExtractionEvent,
    ExtractionEventType,
    ExtractionStage,
    ExtractionProgress,
    ExtractionEventData,
)
from app.core import get_logger
from app.core.exceptions import FileParseFailed, ExtractionFailed

logger = get_logger(__name__)

# Sentinel value that signals the stream is finished
_STREAM_DONE = object()


class Phase1Pipeline:
    """
    LangGraph pipeline for Phase 1: rules extraction.

    Flow: parse_input → segment_content → orchestrate_extraction → finalize_rules

    Supports two execution modes:
      - run()    : standard async call, returns list[dict] when complete
      - stream() : async generator, yields ExtractionEvent objects in real-time
    """

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider
        self._pdf_parser = PDFParser()
        self._docx_parser = DOCXParser()
        self._text_parser = TextParser()
        self._graph = self._build_graph()
        self._event_queue: Optional[asyncio.Queue] = None

    # ------------------------------------------------------------------
    # Event emission
    # ------------------------------------------------------------------

    def _emit(self, event: ExtractionEvent) -> None:
        """Put an event into the queue (non-blocking, safe from sync or async context)."""
        logger.debug(f"[SSE] {event.event_type} | {event.stage} | {event.message}")
        if self._event_queue is not None:
            self._event_queue.put_nowait(event)

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

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.parsing_started,
            stage=ExtractionStage.parsing,
            message="Reading document...",
        ))

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

            char_count = len(text)
            logger.info(f"Document parsed: {char_count} chars")

            self._emit(ExtractionEvent(
                event_type=ExtractionEventType.parsing_complete,
                stage=ExtractionStage.parsing,
                message=f"Document parsed: {char_count:,} characters",
                data=ExtractionEventData(char_count=char_count),
            ))

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

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.segmentation_started,
            stage=ExtractionStage.segmentation,
            message="Analyzing document structure...",
        ))

        segments = segment_text(parsed_text)
        section_titles = [seg.title for seg in segments if seg.title]

        logger.info(f"Content segmented into {len(segments)} sections")

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.segmentation_complete,
            stage=ExtractionStage.segmentation,
            message=f"Found {len(segments)} logical sections",
            data=ExtractionEventData(
                section_count=len(segments),
                section_titles=section_titles,
            ),
        ))

        return {"segments": segments}

    async def _orchestrate_extraction(self, state: Phase1State) -> dict:
        """Fan-out: parallel LLM extraction per segment. Fan-in: aggregate candidates."""
        segments: list[DocumentSegment] = state.get("segments", [])
        total = len(segments)

        if not total:
            logger.warning("No segments to process — returning empty candidates")
            return {"rule_candidates": []}

        logger.info(f"Dispatching {total} segment workers")

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.extraction_started,
            stage=ExtractionStage.extraction,
            message=f"Starting rule extraction from {total} sections...",
            progress=ExtractionProgress(current=0, total=total, percent=0),
        ))

        # Track progress across concurrent workers (asyncio is single-threaded,
        # but lock avoids any ordering issues when multiple workers complete close together)
        completed = 0
        total_candidates_so_far = 0
        progress_lock = asyncio.Lock()

        async def worker_with_emit(segment: DocumentSegment) -> list[RuleCandidate]:
            nonlocal completed, total_candidates_so_far
            candidates = await self._worker_extract(segment)

            async with progress_lock:
                completed += 1
                total_candidates_so_far += len(candidates)
                segment_label = segment.title or f"Section {segment.index + 1}"

                self._emit(ExtractionEvent(
                    event_type=ExtractionEventType.extraction_progress,
                    stage=ExtractionStage.extraction,
                    message=f'Processed "{segment_label}"',
                    progress=ExtractionProgress(
                        current=completed,
                        total=total,
                        percent=round(completed / total * 100),
                    ),
                    data=ExtractionEventData(
                        segment_index=segment.index,
                        segment_title=segment_label,
                        rules_in_segment=len(candidates),
                        total_rules_so_far=total_candidates_so_far,
                    ),
                ))

            return candidates

        tasks = [worker_with_emit(seg) for seg in segments]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_candidates: list[RuleCandidate] = []
        failed_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_count += 1
                logger.error(f"Worker for segment {i} failed (already logged with traceback above)")
            else:
                all_candidates.extend(result)

        logger.info(
            f"Orchestration complete: {len(all_candidates)} raw candidates, "
            f"{failed_count}/{total} segments failed"
        )

        summary = f"Extracted {len(all_candidates)} rule candidates from {total - failed_count} sections"
        if failed_count:
            summary += f" ({failed_count} section{'s' if failed_count > 1 else ''} failed)"

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.extraction_complete,
            stage=ExtractionStage.extraction,
            message=summary,
            data=ExtractionEventData(
                total_rules=len(all_candidates),
                failed_segments=failed_count,
            ),
        ))

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
        except Exception:
            logger.exception(f"Worker failed for segment {segment.index} ({segment.title!r})")
            raise

    def _finalize_rules(self, state: Phase1State) -> dict:
        """Deduplicate candidates, assign IDs, and serialize to dicts"""
        candidates: list[RuleCandidate] = state.get("rule_candidates", [])

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.finalization_started,
            stage=ExtractionStage.finalization,
            message="Deduplicating and finalizing rules...",
        ))

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

        self._emit(ExtractionEvent(
            event_type=ExtractionEventType.finalization_complete,
            stage=ExtractionStage.finalization,
            message=f"Complete — {len(rules)} rules extracted",
            progress=ExtractionProgress(percent=100),
            data=ExtractionEventData(
                total_rules=len(candidates),
                unique_rules=len(rules),
                extracted_rules=rules,
            ),
        ))

        return {"extracted_rules": rules}

    # ------------------------------------------------------------------
    # Public API — standard (non-streaming)
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

        logger.info(f"Phase1Pipeline.run starting: input_type={input_type}")
        result = await self._graph.ainvoke(initial_state)

        if result.get("errors"):
            logger.warning(f"Pipeline finished with warnings: {result['errors']}")

        rules = result.get("extracted_rules", [])
        logger.info(f"Phase1Pipeline.run complete: {len(rules)} rules returned")
        return rules

    # ------------------------------------------------------------------
    # Public API — streaming (SSE)
    # ------------------------------------------------------------------

    async def stream(
        self,
        input_type: str,
        raw_file_bytes: Optional[bytes] = None,
        raw_filename: Optional[str] = None,
        raw_text: Optional[str] = None,
    ) -> AsyncIterator[ExtractionEvent]:
        """
        Execute the Phase 1 pipeline and yield ExtractionEvent objects in real-time.

        Events are emitted at each pipeline milestone. The final event
        (finalization_complete) includes the full extracted_rules list.

        Usage:
            async for event in pipeline.stream(...):
                yield ServerSentEvent(data=event.model_dump_json())
        """
        queue: asyncio.Queue = asyncio.Queue()
        self._event_queue = queue

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

        async def _run_pipeline():
            try:
                logger.info(f"Phase1Pipeline.stream starting: input_type={input_type}")
                await self._graph.ainvoke(initial_state)
            except Exception as e:
                logger.error(f"Pipeline stream error: {e}")
                queue.put_nowait(ExtractionEvent(
                    event_type=ExtractionEventType.error,
                    stage=ExtractionStage.parsing,
                    message=str(e),
                ))
            finally:
                queue.put_nowait(_STREAM_DONE)

        task = asyncio.create_task(_run_pipeline())

        try:
            while True:
                item = await queue.get()
                if item is _STREAM_DONE:
                    break
                yield item
        finally:
            await task
            self._event_queue = None
