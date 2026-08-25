from typing import Optional
from pydantic import Field
from .common import SchemaBase, UserRole


class LoginRequest(SchemaBase):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)


class UserDto(SchemaBase):
    id: int
    email: str
    full_name: str = Field(..., serialization_alias="fullName", alias="fullName")
    role: UserRole


class LoginResponse(SchemaBase):
    access_token: str = Field(..., serialization_alias="accessToken", alias="accessToken")
    token_type: str = Field(default="Bearer", serialization_alias="tokenType", alias="tokenType")
    expires_in: int = Field(default=7200, serialization_alias="expiresIn", alias="expiresIn")
    user: UserDto
