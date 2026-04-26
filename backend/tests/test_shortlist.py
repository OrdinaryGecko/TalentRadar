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
            base_match_score=result.match_score,
            match_score=adjusted_match_score,
            match_adjustment=round(adjusted_match_score - result.match_score, 1),
            explanation=result.explanation,
            conversation=conversation,
            interest=interest,
        )
        for result in matched
        for conversation, interest, adjusted_match_score in [await simulator.run(
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


@pytest.mark.anyio
async def test_shortlist_endpoint_accepts_custom_candidate_pool() -> None:
    custom_candidates = [
        {
            "id": "custom_001",
            "full_name": "Custom Candidate",
            "headline": "Senior AI engineer with strong FastAPI background",
            "location": "Bengaluru, India",
            "work_mode_preferences": ["remote"],
            "years_experience": 6,
            "current_title": "Senior AI Engineer",
            "current_company": "Custom Labs",
            "skills": ["Python", "FastAPI", "LLMs", "pgvector"],
            "domain_experience": ["SaaS"],
            "summary": "Built retrieval systems and backend AI workflows.",
            "persona": "actively_looking",
            "availability_days": 15,
            "compensation_expectation_lpa": 32,
            "engagement_status": "active",
        }
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/jobs/shortlist",
            json={
                "raw_description": SAMPLE_SHORTLIST_JD,
                "limit": 3,
                "candidates": custom_candidates,
            },
        )

    assert response.status_code == 200
    payload = response.json()

    assert len(payload["results"]) == 1
    assert payload["results"][0]["candidate"]["id"] == "custom_001"
