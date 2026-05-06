# app/services/extraction_service.py
import logging
from app.core.extractor import extract_to_dict
from app.core.schemas import SchemaType

logger = logging.getLogger(__name__)


def extract_from_text(text: str, schema_type: str) -> dict:
    """
    Validate inputs and extract structured data from text.
    This is the single public entry point for the API routes.

    Args:
        text: Raw unstructured text
        schema_type: String name of the schema type

    Returns:
        Dict containing extracted_data and metadata
    """
    # Validate schema type string → enum
    try:
        schema_enum = SchemaType(schema_type)
    except ValueError:
        valid = [s.value for s in SchemaType]
        raise ValueError(
            f"Invalid schema type '{schema_type}'. "
            f"Must be one of: {valid}"
        )

    # Validate text length
    if len(text.strip()) < 20:
        raise ValueError(
            "Input text is too short for meaningful extraction. "
            "Please provide at least a paragraph of text."
        )

    if len(text) > 50000:
        raise ValueError(
            "Input text exceeds maximum length of 50,000 characters. "
            "Please split into smaller sections."
        )

    logger.info(
        f"Processing extraction request: schema={schema_type}, "
        f"text_length={len(text)}"
    )

    extracted = extract_to_dict(text=text, schema_type=schema_enum)

    return {
        "schema_type": schema_type,
        "extracted_data": extracted,
        "character_count": len(text),
        "status": "success",
    }