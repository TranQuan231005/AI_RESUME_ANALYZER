from pydantic import Field
from .common import SchemaBase


class ParsedDocument(SchemaBase):
    file_name: str = Field(..., serialization_alias="fileName", alias="fileName")
    text: str = Field(..., min_length=1)
    page_count: int = Field(..., ge=1, serialization_alias="pageCount", alias="pageCount")
    size_bytes: int = Field(
        ...,
        ge=1,
        le=5_242_880,
        serialization_alias="sizeBytes",
        alias="sizeBytes",
    )
