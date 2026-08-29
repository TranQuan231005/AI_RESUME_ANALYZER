from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["Extraction"])

class ExtractRequest(BaseModel):
    file_name: str = Field(alias="fileName")
    text: str
    page_count: int = Field(alias="pageCount")
    size_bytes: int = Field(alias="sizeBytes")

    class Config:
        populate_by_name = True

@router.post("/extract-features")
async def extract_features(payload: ExtractRequest):
    # Stub cho D2 - pipeline xử lý thực tế sẽ tích hợp sau
    return {"status": "success"}