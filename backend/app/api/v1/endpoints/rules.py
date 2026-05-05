from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from datetime import datetime
import uuid

from app.config import Settings, get_settings
from app.core import get_logger, InvalidInputException, FileParseFailed, ExtractionFailed
from app.api.v1.schemas import ExtractRulesResponse, Rule, ErrorResponse
from app.utils.validators import validate_file, validate_text

logger = get_logger(__name__)
router = APIRouter(prefix="/extract-rules", tags=["rules"])


# TODO: Replace with actual rule extraction logic from agents
def extract_rules_from_text(text: str) -> list[Rule]:
    """
    Placeholder for rule extraction logic.
    Will be replaced with LangGraph agent pipeline.
    """
    dummy_rules = [
        Rule(
            id="rule_001",
            title="Employee Background Check",
            description="All employees must undergo a comprehensive background check before employment",
            conditions=["Check must be completed within 30 days of offer"],
            expected_evidence=["Background check report from accredited vendor"],
            section="Section 2: Hiring Procedures",
            severity="high",
            status="extracted"
        ),
        Rule(
            id="rule_002",
            title="Data Confidentiality Agreement",
            description="Every employee must sign a data confidentiality agreement upon joining",
            conditions=["Agreement must be signed before first day of work"],
            expected_evidence=["Signed confidentiality agreement"],
            section="Section 3: Employment Agreements",
            severity="high",
            status="extracted"
        )
    ]
    return dummy_rules


@router.post(
    "",
    response_model=ExtractRulesResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def extract_rules(
    file: UploadFile = File(None),
    text: str = Form(None),
    settings: Settings = Depends(get_settings)
) -> ExtractRulesResponse:
    """
    Extract structured rules from a document.

    Accepts either a file upload (PDF/DOCX) or text input.
    Returns a structured list of rules with conditions and expected evidence.

    Args:
        file: PDF or DOCX file upload (optional)
        text: Raw text input (optional)
        settings: Application settings

    Returns:
        ExtractRulesResponse with extracted rules

    Raises:
        HTTPException 400: Invalid input (neither file nor text provided)
        HTTPException 422: File parsing failed
        HTTPException 500: Rules extraction failed
    """
    try:
        document_id = str(uuid.uuid4())
        logger.info(f"Processing extract-rules request: {document_id}")

        # Validate that either file or text is provided
        if not file and not text:
            raise InvalidInputException("Either file or text input must be provided")

        extracted_text = None

        # Process file input
        if file:
            try:
                validate_file(file.filename, file.size, settings.max_file_size_mb)
                logger.debug(f"File validation passed: {file.filename}")

                # TODO: Implement actual file parsing
                # For now, read text from file
                if file.filename.endswith('.txt'):
                    extracted_text = (await file.read()).decode('utf-8')
                else:
                    raise FileParseFailed(
                        "File parsing not yet implemented",
                        file_type=file.filename.split('.')[-1]
                    )
            except FileParseFailed:
                raise
            except Exception as e:
                logger.error(f"File processing error: {str(e)}")
                raise FileParseFailed(str(e), file_type=file.filename.split('.')[-1])

        # Process text input
        if text:
            try:
                validate_text(text, settings.max_text_length)
                extracted_text = text
                logger.debug("Text validation passed")
            except InvalidInputException:
                raise

        # Extract rules from the document text
        if extracted_text:
            try:
                rules = extract_rules_from_text(extracted_text)
                logger.info(f"Successfully extracted {len(rules)} rules: {document_id}")

                return ExtractRulesResponse(
                    document_id=document_id,
                    total_rules=len(rules),
                    rules=rules,
                    extraction_timestamp=datetime.utcnow().isoformat() + "Z",
                    status="success"
                )
            except Exception as e:
                logger.error(f"Rules extraction failed: {str(e)}")
                raise ExtractionFailed(str(e))

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
        logger.error(f"Unexpected error in extract_rules: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
