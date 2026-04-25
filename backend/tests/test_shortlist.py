import pytest
from httpx import ASGITransport, AsyncClient

from app.jd_parser import JobDescriptionParser
from app.main import app
from app.matcher import CandidateMatcher
from app.outreach import OutreachSimulator
from app.repository import load_candidate_fixture
from app.shortlist import ShortlistRanker


SAMPLE_SHORTLIST_JD = """
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
async def test_shortlist_ranker_combines_match_and_interest() -> None:
    parsed_job = JobDescriptionParser().parse(SAMPLE_SHORTLIST_JD)
    matched = await CandidateMatcher().rank_candidates(
        parsed_job=parsed_job,
        candidates=load_candidate_fixture(),
        limit=3,
    )

    simulator = OutreachSimulator()
    from app.models import OutreachResult

    payload = [
        OutreachResult(
            candidate=result.candidate,
            match_score=result.match_score,
            explanation=result.explanation,
            conversation=conversation,
            interest=interest,
        )
        for result in matched
        for conversation, interest in [simulator.run(
            parsed_job=parsed_job,
            candidate_result=result,
        )]
    ]
    shortlist = ShortlistRanker().rank(payload)

    assert len(shortlist) == 3
    assert shortlist[0].combined_score >= shortlist[1].combined_score
    expected_score = round(
        shortlist[0].match_score * 0.65 + shortlist[0].interest_score * 0.35,
        1,
    )
    assert shortlist[0].combined_score == expected_score
    assert shortlist[0].candidate.id in {"cand_001", "cand_002"}


@pytest.mark.anyio
async def test_shortlist_endpoint_returns_ranked_output() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/jobs/shortlist",
            json={"raw_description": SAMPLE_SHORTLIST_JD, "limit": 3},
        )

    assert response.status_code == 200
    payload = response.json()

    assert payload["parsed_job"]["title"] == "Senior AI Engineer"
    assert len(payload["results"]) == 3
    assert payload["results"][0]["combined_score"] >= payload["results"][1]["combined_score"]
    assert "interest_score" in payload["results"][0]
