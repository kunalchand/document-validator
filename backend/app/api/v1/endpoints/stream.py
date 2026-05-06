from typing import Annotated, AsyncIterator, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from app.agents.events import ExtractionEvent, ExtractionEventType, ExtractionStage
from app.api.v1.schemas import ErrorResponse
from app.config import Settings, get_settings
from app.core import get_logger, FileParseFailed, InvalidInputException
from app.pipeline.phase1_graph import Phase1Pipeline
from app.providers.factory import ProviderFactory
from app.utils.validators import validate_file, validate_text

logger = get_logger(__name__)
router = APIRouter(prefix="/extract-rules-stream", tags=["streaming"])

# SSE retry interval sent to clients (ms) — browser will reconnect after this delay
_SSE_RETRY_MS = 5000


def _get_pipeline(settings: Settings) -> Phase1Pipeline:
    provider = ProviderFactory.create_llm_provider(
        provider_type=settings.llm_provider,
        api_key=settings.llm_api_key or "",
        config={"model": settings.llm_model, "host": settings.ollama_host},
    )
    return Phase1Pipeline(llm_provider=provider)


def _make_sse(event: ExtractionEvent, event_id: int) -> ServerSentEvent:
    """Serialize an ExtractionEvent into a ServerSentEvent frame"""
    return ServerSentEvent(
        data=event.model_dump_json(exclude={"event_id"}),
        event=event.event_type.value,
        id=str(event_id),
        retry=_SSE_RETRY_MS,
    )


@router.post(
    "",
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Extract rules with real-time progress streaming (SSE)",
    description=(
        "Runs the Phase 1 extraction pipeline and streams progress events using "
        "Server-Sent Events. Connect with EventSource or fetch() + ReadableStream. "
        "The final `finalization_complete` event includes the full extracted_rules list. "
        "Supports Last-Event-ID header for SSE spec compliance (stateless restart only)."
    ),
)
async def extract_rules_stream(
    request: Request,
    file: Annotated[Optional[UploadFile], File()] = None,
    text: Annotated[Optional[str], Form()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> EventSourceResponse:
    """
    POST /api/v1/extract-rules-stream

    Input validation and file reading happen BEFORE the SSE response is opened,
    so HTTP 400/422 errors are returned as standard JSON (not SSE error events)
    when the request itself is invalid.

    Once the SSE stream starts, pipeline errors are delivered as error events.
    """
    # --- Validate and read all inputs before opening the stream ---
    if not file and not text:
        raise HTTPException(
            status_code=400,
            detail="Either a file upload or text input must be provided",
        )

    file_bytes: Optional[bytes] = None
    input_type = "text"
    raw_filename: Optional[str] = None
    raw_text = text

    if file:
        try:
            validate_file(file.filename, file.size, settings.max_file_size_mb)
        except InvalidInputException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)

        file_bytes = await file.read()
        filename_lower = (file.filename or "").lower()

        if filename_lower.endswith(".pdf"):
            input_type = "pdf"
        elif filename_lower.endswith((".docx", ".doc")):
            input_type = "docx"
        elif filename_lower.endswith(".txt"):
            input_type = "text"
            raw_text = file_bytes.decode("utf-8", errors="replace")
            file_bytes = None
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: PDF, DOCX, TXT",
            )

        raw_filename = file.filename

    elif text:
        try:
            validate_text(text, settings.max_text_length)
        except InvalidInputException as e:
            raise HTTPException(status_code=e.status_code, detail=e.message)

    # Last-Event-ID: SSE spec — client sends this on reconnect.
    # We honour it for ID sequencing continuity; full pipeline replay isn't supported
    # for file uploads (file bytes aren't retained server-side).
    last_event_id_header = request.headers.get("last-event-id")
    starting_event_id = int(last_event_id_header) if last_event_id_header else 0

    pipeline = _get_pipeline(settings)

    logger.info(f"SSE stream opened: input_type={input_type}")

    async def event_generator() -> AsyncIterator[ServerSentEvent]:
        event_id = starting_event_id

        try:
            async for event in pipeline.stream(
                input_type=input_type,
                raw_file_bytes=file_bytes,
                raw_filename=raw_filename,
                raw_text=raw_text,
            ):
                event_id += 1
                event.event_id = str(event_id)
                yield _make_sse(event, event_id)

        except FileParseFailed as e:
            logger.warning(f"SSE stream: file parse failed: {e.message}")
            yield ServerSentEvent(
                data=ExtractionEvent(
                    event_type=ExtractionEventType.error,
                    stage=ExtractionStage.parsing,
                    message=e.message,
                ).model_dump_json(),
                event="error",
            )
        except Exception as e:
            logger.error(f"SSE stream: unexpected error: {e}")
            yield ServerSentEvent(
                data=ExtractionEvent(
                    event_type=ExtractionEventType.error,
                    stage=ExtractionStage.parsing,
                    message="An unexpected error occurred during extraction",
                ).model_dump_json(),
                event="error",
            )

        logger.info(f"SSE stream closed: {event_id} events sent")

    return EventSourceResponse(event_generator())
