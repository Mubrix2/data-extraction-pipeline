# app/core/file_parser.py
import io
import logging
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

SUPPORTED_CONTENT_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}


def parse_file(file_bytes: bytes, content_type: str, filename: str) -> str:
    """
    Extract plain text from an uploaded file.
    Supports PDF, DOCX, and TXT. Never writes to disk.

    Returns the full text as a single string.
    Raises ValueError for unsupported types or empty files.
    """
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValueError(
            f"Unsupported file type: {content_type}. "
            f"Accepted formats: PDF, DOCX, TXT"
        )

    file_type = SUPPORTED_CONTENT_TYPES[content_type]
    logger.info(f"Parsing {file_type.upper()}: '{filename}'")

    if file_type == "pdf":
        return _parse_pdf(file_bytes, filename)
    elif file_type == "docx":
        return _parse_docx(file_bytes, filename)
    else:
        return _parse_txt(file_bytes, filename)


def _parse_pdf(file_bytes: bytes, filename: str) -> str:
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())

    if not pages:
        raise ValueError(
            f"No readable text found in '{filename}'. "
            "The PDF may be scanned or image-based."
        )

    return "\n\n".join(pages)


def _parse_docx(file_bytes: bytes, filename: str) -> str:
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        raise ValueError(f"No readable text found in '{filename}'")

    return "\n\n".join(paragraphs)


def _parse_txt(file_bytes: bytes, filename: str) -> str:
    try:
        text = file_bytes.decode("utf-8").strip()
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1").strip()

    if not text:
        raise ValueError(f"Text file '{filename}' is empty")

    return text