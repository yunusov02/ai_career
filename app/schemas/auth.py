"""Phone OTP and JWT authentication schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def normalize_phone(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if len(digits) == 9:
        digits = f"998{digits}"
    if len(digits) != 12 or not digits.startswith("998"):
        raise ValueError("Phone number must be an Uzbekistan number")
    return digits


class OtpRequest(BaseModel):
    phone_number: str
    language: Literal["uz", "ru", "en"] = "uz"

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)


class OtpRequestResponse(BaseModel):
    message: str
    expires_in: int
    retry_after: int


class OtpVerifyRequest(BaseModel):
    phone_number: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    language: Literal["uz", "ru", "en"] = "uz"

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PlatformUserResponse(BaseModel):
    id: int
    phone_number: str
    preferred_language: str
    is_admin: bool
    created_at: datetime
