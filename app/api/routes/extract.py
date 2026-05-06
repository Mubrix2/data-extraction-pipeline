# app/api/routes/extract.py
import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from app.api.schemas import (
    ExtractionResponse,
    FileExtractionResponse,
    SchemaInfo,
    SchemaListResponse,
    TextExtractionRequest,
)
from app.core.schemas import SCHEMA_DESCRIPTIONS
from app.core.file_parser import parse_file, SUPPORTED_CONTENT_TYPES
from app.services.extraction_service import extract_from_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/extract", tags=["Extraction"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


@router.get(
    "/schemas",
    response_model=SchemaListResponse,
    summary="List all available extraction schemas",
)
async def list_schemas():
    """Return all supported schema types and their descriptions."""
    schemas = [
        SchemaInfo(schema_type=s.value, description=d)
        for s, d in SCHEMA_DESCRIPTIONS.items()
    ]
    return SchemaListResponse(schemas=schemas)


@router.post(
    "/text",
    response_model=ExtractionResponse,
    summary="Extract structured data from plain text",
)
async def extract_from_text_endpoint(request: TextExtractionRequest):
    """
    Paste any unstructured text and receive structured JSON.
    Choose a schema type to define what to extract.
    """
    try:
        result = extract_from_text(
            text=request.text,
            schema_type=request.schema_type.value,
        )
        return ExtractionResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extraction failed. Please try again.",
        )


@router.post(
    "/file",
    response_model=FileExtractionResponse,
    summary="Extract structured data from an uploaded file",
)
async def extract_from_file(
    file: UploadFile = File(...),
    schema_type: str = Form(...),
):
    """
    Upload a PDF, DOCX, or TXT file and receive structured JSON.
    File is parsed in memory — never written to disk.
    """
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Accepted: PDF, DOCX, TXT",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds maximum size of 10MB",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    try:
        text = parse_file(
            file_bytes=file_bytes,
            content_type=file.content_type,
            filename=file.filename,
        )

        result = extract_from_text(text=text, schema_type=schema_type)

        return FileExtractionResponse(
            schema_type=result["schema_type"],
            extracted_data=result["extracted_data"],
            filename=file.filename,
            character_count=result["character_count"],
            status=result["status"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"File extraction failed for '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extraction failed. Please try again.",
        )