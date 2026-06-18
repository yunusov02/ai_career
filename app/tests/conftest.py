"""Shared API test fixtures."""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.exceptions import AIServiceError
from app.db.base import Base
from app.main import app


class OfflineAdvisor:
    async def analyze_assessment(self, answers):
        raise AIServiceError(message="Offline test")

    async def generate_learning_path(self, request):
        raise AIServiceError(message="Offline test")

    async def chat_about_module(self, request):
        raise AIServiceError(message="Offline test")


@pytest.fixture(autouse=True)
def offline_advisor(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.guide.get_career_advisor",
        lambda: OfflineAdvisor(),
    )


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear in-memory rate limit counters before each test so tests don't share quota."""
    from app.core.limiter import limiter
    storage = getattr(limiter, "_storage", None)
    if storage is not None:
        reset_fn = getattr(storage, "reset", None) or getattr(storage, "clear", None)
        if callable(reset_fn):
            reset_fn()
    yield


@pytest_asyncio.fixture
async def database():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    yield session_maker
    app.dependency_overrides.clear()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def otp_codes(monkeypatch):
    codes: dict[str, str] = {}

    async def capture_code(self, phone_number: str, code: str, language: str):
        codes[phone_number] = code

    monkeypatch.setattr("app.services.sms_service.SmsService.send_otp", capture_code)
    return codes


@pytest_asyncio.fixture
async def client(database) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as api_client:
        yield api_client


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient, otp_codes: dict[str, str]) -> dict[str, str]:
    phone_number = "998901234567"
    request = await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": phone_number, "language": "uz"},
    )
    assert request.status_code == 200
    response = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": phone_number,
            "code": otp_codes[phone_number],
            "language": "uz",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
