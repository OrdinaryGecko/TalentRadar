import pytest
from httpx import ASGITransport, AsyncClient

from app.jd_parser import JobDescriptionParser
from app.main import app
from app.matcher import CandidateMatcher
from app.repository import load_candidate_fixture


SAMPLE_MATCH_JD = """
Senior AI Engineer
Seniority: senior
Location: India
Work mode: Remote

Requirements:
- 5+ years of experience
- Python
- FastAPI
- LLMs
- pgvector

Nice to have:
- AWS
""".strip()


@pytest.mark.anyio
async def test_matcher_ranks_best_profile_first() -> None:
    parsed_job = JobDescriptionParser().parse(SAMPLE_MATCH_JD)
    results = await CandidateMatcher().rank_candidates(
        parsed_job=parsed_job,
        candidates=load_candidate_fixture(),
        limit=3,
    )

    assert len(results) == 3
    assert results[0].candidate.id == "cand_001"
    assert results[0].match_score > results[1].match_score
    assert "Python" in results[0].explanation.matched_capabilities
    assert "pgvector" in results[0].explanation.matched_capabilities
    assert results[0].match_score == 90.0
    assert "AWS" in results[0].explanation.missing_preferred_capabilities
    assert results[0].explanation.summary


@pytest.mark.anyio
async def test_match_endpoint_returns_ranked_results() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/jobs/match",
            json={"raw_description": SAMPLE_MATCH_JD, "limit": 2},
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["parsed_job"]["title"] == "Senior AI Engineer"
    assert len(payload["results"]) == 2
    assert payload["results"][0]["candidate"]["id"] == "cand_001"
    assert payload["results"][0]["match_score"] >= payload["results"][1]["match_score"]
    assert payload["results"][0]["match_score"] == 90.0
    assert payload["results"][0]["explanation"]["provider"] == "local"
