from typing import Annotated, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException

import uuid

from app.config import Settings, get_settings
from app.core import get_logger, InvalidInputException, FileParseFailed, ExtractionFailed
from app.api.v1.schemas import ExtractRulesResponse, ErrorResponse
from app.utils.validators import validate_file, validate_text
from app.providers.factory import ProviderFactory
from app.pipeline.phase1_graph import Phase1Pipeline

logger = get_logger(__name__)
router = APIRouter(prefix="/extract-rules", tags=["rules"])


def _get_pipeline(settings: Settings) -> Phase1Pipeline:
    """Create a Phase1Pipeline from current settings"""
    provider = ProviderFactory.create_llm_provider(
        provider_type=settings.llm_provider,
        api_key=settings.llm_api_key or "",
        config={"model": settings.llm_model},
    )
    return Phase1Pipeline(llm_provider=provider)


@router.post(
    "",
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def extract_rules(
    file: Annotated[Optional[UploadFile], File()] = None,
    text: Annotated[Optional[str], Form()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> ExtractRulesResponse:
    """
    Extract structured compliance rules from a document.

    Accepts either a file upload (PDF / DOCX) or raw text.
    Runs the Phase 1 LangGraph pipeline: parse → segment → LLM extraction → aggregate.

    Returns:
        ExtractRulesResponse with structured rules and metadata.

    Raises:
        400: Neither file nor text provided, or input is invalid.
        422: File cannot be parsed.
        500: Rules extraction failed unexpectedly.
    """
    try:
        document_id = str(uuid.uuid4())
        logger.info(f"extract-rules request started: document_id={document_id}")

        if not file and not text:
            raise InvalidInputException("Either a file upload or text input must be provided")

        pipeline = _get_pipeline(settings)
        rule_dicts: list[dict] = []

        if file:
            validate_file(file.filename, file.size, settings.max_file_size_mb)
            logger.debug(f"File validated: {file.filename}")

            file_bytes = await file.read()
            filename_lower = (file.filename or "").lower()

            if filename_lower.endswith(".pdf"):
                input_type = "pdf"
            elif filename_lower.endswith((".docx", ".doc")):
                input_type = "docx"
            elif filename_lower.endswith(".txt"):
                rule_dicts = await pipeline.run(
                    input_type="text",
                    raw_text=file_bytes.decode("utf-8", errors="replace"),
                )
                logger.info(f"Extracted {len(rule_dicts)} rules from text file: document_id={document_id}")
                return _build_response(document_id, rule_dicts)
            else:
                raise InvalidInputException(
                    f"Unsupported file type: {filename_lower.split('.')[-1]}. "
                    "Supported types: PDF, DOCX, TXT"
                )

            rule_dicts = await pipeline.run(
                input_type=input_type,
                raw_file_bytes=file_bytes,
                raw_filename=file.filename,
            )

        elif text:
            validate_text(text, settings.max_text_length)
            logger.debug("Text input validated")
            rule_dicts = await pipeline.run(input_type="text", raw_text=text)

        logger.info(f"Extraction complete: {len(rule_dicts)} rules, document_id={document_id}")
        return _build_response(document_id, rule_dicts)

    except InvalidInputException as e:
        logger.warning(f"Invalid input: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except FileParseFailed as e:
        logger.warning(f"File parse failed: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ExtractionFailed as e:
        logger.error(f"Extraction failed: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in extract_rules: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def _build_response(document_id: str, rules: list[dict]) -> ExtractRulesResponse:
    return ExtractRulesResponse(
        document_id=document_id,
        total_rules=len(rules),
        rules=rules,
        extraction_timestamp=datetime.now(timezone.utc).isoformat(),
        status="success",
    )
