import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.repository import load_candidate_fixture


def test_seed_fixture_loads_profiles() -> None:
    candidates = load_candidate_fixture()

    assert len(candidates) == 8
    assert candidates[0].id == "cand_001"


@pytest.mark.anyio
async def test_list_candidates_returns_seeded_profiles() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/candidates")

    assert response.status_code == 200

    payload = response.json()

    assert payload["count"] == 8
    assert payload["items"][0]["full_name"] == "Aditi Rao"


@pytest.mark.anyio
async def test_get_candidate_returns_candidate_details() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/candidates/cand_004")

    assert response.status_code == 200
    assert response.json()["current_company"] == "OpsHarbor"


@pytest.mark.anyio
async def test_get_candidate_returns_not_found_for_unknown_id() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/candidates/cand_999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Candidate not found"}
