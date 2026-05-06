# frontend/api_client.py
import requests
from config import API_BASE_URL

TIMEOUT = (3, 60)  # (connect timeout, read timeout)


def get_schemas() -> dict:
    try:
        r = requests.get(f"{API_BASE_URL}/api/v1/extract/schemas", timeout=10)
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the API. Is it running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_text(text: str, schema_type: str) -> dict:
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/extract/text",
            json={"text": text, "schema_type": schema_type},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the API."}
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        return {"success": False, "error": detail}


def extract_file(file_bytes: bytes, filename: str, content_type: str, schema_type: str) -> dict:
    try:
        r = requests.post(
            f"{API_BASE_URL}/api/v1/extract/file",
            files={"file": (filename, file_bytes, content_type)},
            data={"schema_type": schema_type},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return {"success": True, "data": r.json()}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to the API."}
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        return {"success": False, "error": detail}


def check_health() -> bool:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False