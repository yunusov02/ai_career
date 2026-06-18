"""OTP and JWT authentication integration tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_otp_login_and_refresh(client: AsyncClient, otp_codes: dict[str, str]):
    phone_number = "998901112233"
    requested = await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": phone_number, "language": "uz"},
    )

    assert requested.status_code == 200
    assert "code" not in requested.json()
    assert phone_number in otp_codes

    verified = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": phone_number,
            "code": otp_codes[phone_number],
            "language": "uz",
        },
    )
    assert verified.status_code == 200
    tokens = verified.json()

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["phone_number"] == phone_number

    refreshed = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]


@pytest.mark.asyncio
async def test_invalid_otp_attempts_are_persisted(client: AsyncClient, otp_codes: dict[str, str]):
    phone_number = "998909998877"
    await client.post(
        "/api/v1/auth/request-otp",
        json={"phone_number": phone_number, "language": "uz"},
    )

    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/verify-otp",
            json={"phone_number": phone_number, "code": "000000", "language": "uz"},
        )
        assert response.status_code == 401

    locked = await client.post(
        "/api/v1/auth/verify-otp",
        json={
            "phone_number": phone_number,
            "code": otp_codes[phone_number],
            "language": "uz",
        },
    )
    assert locked.status_code == 401
    assert locked.json()["detail"] == "Too many verification attempts"
