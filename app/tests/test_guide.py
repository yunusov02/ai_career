"""Authenticated career guide integration tests."""

import pytest
from httpx import AsyncClient


def guide_payload() -> dict:
    return {
        "language": "uz",
        "interests": ["it", "finance"],
        "answers": [
            {
                "question": f"Assessment statement {index}",
                "category": "logic",
                "score": 4,
            }
            for index in range(1, 26)
        ],
    }


@pytest.mark.asyncio
async def test_guide_cors_preflight(client: AsyncClient):
    response = await client.options(
        "/api/v1/guide/analyze",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"


@pytest.mark.asyncio
async def test_guide_requires_authentication(client: AsyncClient):
    response = await client.post("/api/v1/guide/analyze", json=guide_payload())

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_guide_returns_three_careers(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/guide/analyze",
        json=guide_payload(),
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_careers"]) == 3
    reasons = [career["reason"] for career in data["recommended_careers"]]
    assert len(set(reasons)) == 3
    assert "4.0/5" in reasons[0]
    history = await client.get("/api/v1/history", headers=auth_headers)
    assert len(history.json()["assessments"]) == 1


@pytest.mark.asyncio
async def test_guide_requires_exactly_twenty_five_answers(client: AsyncClient, auth_headers):
    payload = guide_payload()
    payload["answers"] = payload["answers"][:-1]

    response = await client.post(
        "/api/v1/guide/analyze",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_learning_path_contains_modules_resources_and_quizzes(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/guide/learning-path",
        json={
            "language": "uz",
            "career_name": "Software Engineer",
            "career_reason": "Strong technical and problem-solving fit.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["modules"]) >= 5
    assert all(module["resources"] for module in data["modules"])
    assert all(len(module["quiz"]) == 5 for module in data["modules"])
    assert all(
        len({question["question"] for question in module["quiz"]}) == 5
        for module in data["modules"]
    )
    assert data["id"]


@pytest.mark.asyncio
async def test_module_chat_returns_contextual_answer(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/guide/chat",
        json={
            "language": "uz",
            "career_name": "Software Engineer",
            "module_title": "Python Foundations",
            "module_context": "Variables, loops, functions, and debugging.",
            "messages": [{"role": "user", "content": "Python function nima?"}],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert "return" in response.json()["answer"]
    assert response.json()["suggested_questions"]
