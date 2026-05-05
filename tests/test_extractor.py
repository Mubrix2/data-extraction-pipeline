# tests/test_extractor.py
import pytest
from unittest.mock import patch, MagicMock
from app.core.schemas import SchemaType, SCHEMA_REGISTRY
from app.services.extraction_service import extract_from_text


def test_schema_registry_has_four_schemas():
    assert len(SCHEMA_REGISTRY) == 4


def test_all_schema_types_in_registry():
    for schema_type in SchemaType:
        assert schema_type in SCHEMA_REGISTRY


def test_extract_invalid_schema_type():
    with pytest.raises(ValueError, match="Invalid schema type"):
        extract_from_text("some longer text here for testing", "invalid_schema")


def test_extract_text_too_short():
    with pytest.raises(ValueError, match="too short"):
        extract_from_text("hi", "job_posting")


def test_extract_text_too_long():
    with pytest.raises(ValueError, match="maximum length"):
        extract_from_text("x" * 50001, "job_posting")


@patch("app.services.extraction_service.extract_to_dict")
def test_extract_job_posting_success(mock_extract):
    mock_extract.return_value = {
        "job_title": "Python Engineer",
        "company_name": "Flutterwave",
        "location": "Lagos, Nigeria",
        "summary": "Senior engineering role at a leading fintech.",
        "requirements": [],
        "responsibilities": [],
        "benefits": [],
    }
    result = extract_from_text(
        text="We are hiring a Python Engineer at Flutterwave Lagos Nigeria.",
        schema_type="job_posting",
    )
    assert result["status"] == "success"
    assert result["schema_type"] == "job_posting"
    assert result["extracted_data"]["job_title"] == "Python Engineer"
    assert result["character_count"] > 0


@patch("app.services.extraction_service.extract_to_dict")
def test_extract_news_article_success(mock_extract):
    mock_extract.return_value = {
        "headline": "Moniepoint raises $110M",
        "summary": "Nigerian fintech raised Series C funding.",
        "sentiment": "positive",
        "key_entities": [],
        "topics": ["fintech", "funding"],
        "key_facts": ["$110M raised"],
    }
    result = extract_from_text(
        text="Nigerian fintech Moniepoint has raised $110 million in a Series C round.",
        schema_type="news_article",
    )
    assert result["status"] == "success"
    assert result["extracted_data"]["sentiment"] == "positive"


@patch("app.services.extraction_service.extract_to_dict")
def test_extract_returns_character_count(mock_extract):
    mock_extract.return_value = {"job_title": "Engineer", "summary": "Good role."}
    sample_text = "We are hiring a Senior Engineer at TechCorp in Abuja Nigeria."
    result = extract_from_text(text=sample_text, schema_type="job_posting")
    assert result["character_count"] == len(sample_text)