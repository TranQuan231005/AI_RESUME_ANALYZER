from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class FieldEnum(str, Enum):
    DATA_SCIENCE = "Data Science"
    WEB_DEVELOPMENT = "Web Development"
    ANDROID_DEVELOPMENT = "Android Development"
    IOS_DEVELOPMENT = "iOS Development"
    UI_UX = "UI/UX"
    UNKNOWN = "Unknown"


class AiProvider(str, Enum):
    OLLAMA = "OLLAMA"
    RULE_BASED = "RULE_BASED"


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    def __getattr__(self, item: str) -> Any:
        try:
            return super().__getattribute__(item)
        except AttributeError:
            fields = object.__getattribute__(self, "__class__").model_fields
            for field_name, field_info in fields.items():
                if field_info.alias == item or field_info.serialization_alias == item:
                    return getattr(self, field_name)
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")


class AiMetadata(SchemaBase):
    provider: AiProvider
    model: str
    used_fallback: bool = Field(..., serialization_alias="usedFallback", alias="usedFallback")
    processing_ms: int = Field(..., ge=0, serialization_alias="processingMs", alias="processingMs")


class ApiError(SchemaBase):
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    status: int
    code: str
    message: str
    path: str
    field_errors: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias="fieldErrors",
        alias="fieldErrors",
    )
    request_id: str = Field(..., serialization_alias="requestId", alias="requestId")


class HealthResponse(SchemaBase):
    status: str = "healthy"
    model: str = "qwen3:4b"
    ollama_reachable: bool = Field(
        default=False,
        serialization_alias="ollamaReachable",
        alias="ollamaReachable",
    )
