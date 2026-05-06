# tests/test_api.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_app

client = TestClient(create_app())


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_schemas_returns_four():
    response = client.get("/api/v1/extract/schemas")
    assert response.status_code == 200
    assert len(response.json()["schemas"]) == 4


def test_list_schemas_contains_expected_types():
    response = client.get("/api/v1/extract/schemas")
    types = [s["schema_type"] for s in response.json()["schemas"]]
    assert "job_posting" in types
    assert "invoice" in types
    assert "contact_info" in types
    assert "news_article" in types


@patch("app.api.routes.extract.extract_from_text")
def test_extract_text_success(mock_extract):
    mock_extract.return_value = {
        "schema_type": "job_posting",
        "extracted_data": {"job_title": "Python Engineer", "summary": "Good role."},
        "character_count": 80,
        "status": "success",
    }
    response = client.post(
        "/api/v1/extract/text",
        json={
            "text": "We are hiring a Python Engineer at TechCorp Lagos Nigeria.",
            "schema_type": "job_posting",
        },
    )
    assert response.status_code == 200
    assert response.json()["extracted_data"]["job_title"] == "Python Engineer"


def test_extract_text_too_short_rejected():
    response = client.post(
        "/api/v1/extract/text",
        json={"text": "hi", "schema_type": "job_posting"},
    )
    assert response.status_code == 422


def test_extract_file_wrong_type_rejected():
    response = client.post(
        "/api/v1/extract/file",
        files={"file": ("data.csv", b"col1,col2\nval1,val2", "text/csv")},
        data={"schema_type": "invoice"},
    )
    assert response.status_code == 415