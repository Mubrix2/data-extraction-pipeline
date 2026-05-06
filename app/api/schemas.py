# app/api/schemas.py
from pydantic import BaseModel, Field
from app.core.schemas import SchemaType


class TextExtractionRequest(BaseModel):
    text: str = Field(
        min_length=20,
        max_length=50000,
        description="The unstructured text to extract from",
    )
    schema_type: SchemaType = Field(
        description="Which extraction schema to apply",
    )


class ExtractionResponse(BaseModel):
    schema_type: str
    extracted_data: dict
    character_count: int
    status: str


class FileExtractionResponse(BaseModel):
    schema_type: str
    extracted_data: dict
    filename: str
    character_count: int
    status: str


class SchemaInfo(BaseModel):
    schema_type: str
    description: str


class SchemaListResponse(BaseModel):
    schemas: list[SchemaInfo]


class HealthResponse(BaseModel):
    status: str
    env: str