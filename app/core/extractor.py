# app/core/extractor.py
import logging
from pydantic import BaseModel
import instructor
from groq import Groq

from app.config import GROQ_API_KEY, LLM_MODEL, TEMPERATURE, MAX_RETRIES
from app.core.schemas import SchemaType, SCHEMA_REGISTRY, SCHEMA_DESCRIPTIONS

logger = logging.getLogger(__name__)

# Lazy singleton — client created once at startup, reused for every request
_client = None


def get_client():
    """Create and cache the Instructor-patched Groq client."""
    global _client
    if _client is None:
        raw_client = Groq(api_key=GROQ_API_KEY)
        _client = instructor.from_groq(raw_client, mode=instructor.Mode.JSON)
        logger.info("Instructor-patched Groq client initialised")
    return _client


def _build_system_prompt(schema_type: SchemaType) -> str:
    """
    Build a precise system prompt for the given schema type.
    The task description comes from SCHEMA_DESCRIPTIONS so it
    stays consistent with what the API advertises to clients.
    """
    return f"""You are a precise data extraction engine. Your only job is to \
extract structured information from the provided text.

Task: {SCHEMA_DESCRIPTIONS[schema_type]}

Rules you must follow without exception:
1. Extract ONLY information that is explicitly present in the text
2. Do not infer, assume, or hallucinate any information
3. Use null for fields where information is not present in the text
4. Extract financial figures and dates exactly as they appear — do not reformat
5. Be thorough — extract every relevant piece of information available
6. Return valid structured data matching the required schema exactly"""


def extract(text: str, schema_type: SchemaType) -> BaseModel:
    """
    Extract structured data from text using the specified schema.

    Args:
        text: The raw unstructured text to extract from
        schema_type: Which extraction schema to apply

    Returns:
        A validated Pydantic model instance with the extracted data

    Raises:
        ValueError: If text is empty or schema type is unknown
        Exception: If extraction fails after all retries
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty")

    if schema_type not in SCHEMA_REGISTRY:
        raise ValueError(f"Unknown schema type: {schema_type}")

    schema_model = SCHEMA_REGISTRY[schema_type]
    client = get_client()

    logger.info(
        f"Extracting '{schema_type.value}' from "
        f"{len(text)} characters of text"
    )

    try:
        result = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": _build_system_prompt(schema_type),
                },
                {
                    "role": "user",
                    "content": (
                        f"Extract structured information from the following "
                        f"text:\n\n{text}"
                    ),
                },
            ],
            response_model=schema_model,
            temperature=TEMPERATURE,
            max_retries=MAX_RETRIES,
        )

        logger.info(f"Extraction successful for schema '{schema_type.value}'")
        return result

    except Exception as e:
        logger.error(
            f"Extraction failed for schema '{schema_type.value}': {e}"
        )
        raise


def extract_to_dict(text: str, schema_type: SchemaType) -> dict:
    """
    Extract and return as a plain dictionary.
    This is what the service layer calls — keeps the service
    layer decoupled from Pydantic model internals.
    """
    result = extract(text, schema_type)
    return result.model_dump()