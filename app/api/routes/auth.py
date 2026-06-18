"""Phone OTP authentication routes."""

from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.limiter import limiter
from app.schemas.auth import (
    OtpRequest,
    OtpRequestResponse,
    OtpVerifyRequest,
    PlatformUserResponse,
    RefreshTokenRequest,
    Token,
)
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/request-otp", response_model=OtpRequestResponse)
@limiter.limit("5/minute")
async def request_otp(request: Request, payload: OtpRequest, db: DbSession):
    try:
        await AuthService(db).request_otp(payload.phone_number, payload.language)
        return OtpRequestResponse(
            message="Verification code sent",
            expires_in=settings.otp_expire_minutes * 60,
            retry_after=settings.otp_resend_seconds,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=exc.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.post("/verify-otp", response_model=Token)
@limiter.limit("10/minute")
async def verify_code(request: Request, payload: OtpVerifyRequest, db: DbSession):
    try:
        _, tokens = await AuthService(db).verify_otp(
            payload.phone_number,
            payload.code,
            payload.language,
        )
        return tokens
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message)


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshTokenRequest, db: DbSession):
    try:
        return await AuthService(db).refresh_token(payload.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message)


@router.get("/me", response_model=PlatformUserResponse)
async def me(current_user: CurrentUser):
    return current_user
