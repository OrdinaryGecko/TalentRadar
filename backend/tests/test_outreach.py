import pytest
from httpx import ASGITransport, AsyncClient

from app.jd_parser import JobDescriptionParser
from app.main import app
from app.matcher import CandidateMatcher
from app.outreach import OutreachSimulator
from app.repository import load_candidate_fixture


SAMPLE_OUTREACH_JD = """
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
async def test_outreach_simulator_generates_conversation_and_interest() -> None:
    parsed_job = JobDescriptionParser().parse(SAMPLE_OUTREACH_JD)
    match_result = (
        await CandidateMatcher().rank_candidates(
            parsed_job=parsed_job,
            candidates=load_candidate_fixture(),
            limit=1,
        )
    )[0]

    conversation, interest, adjusted_match_score = await OutreachSimulator().run(
        parsed_job=parsed_job,
        candidate_result=match_result,
    )

    assert conversation.candidate_id == "cand_001"
    assert len(conversation.transcript) == 4
    assert interest.interest_level in {"high", "medium", "low"}
    assert interest.interest_score > 0
    assert interest.summary
    assert adjusted_match_score >= 0


@pytest.mark.anyio
async def test_outreach_endpoint_returns_interest_results() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/jobs/outreach",
            json={"raw_description": SAMPLE_OUTREACH_JD, "limit": 2},
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["parsed_job"]["title"] == "Senior AI Engineer"
    assert len(payload["results"]) == 2
    assert payload["results"][0]["conversation"]["transcript"][0]["speaker"] == "recruiter"
    assert payload["results"][0]["interest"]["interest_score"] >= 0
    assert "base_match_score" in payload["results"][0]
    assert "match_adjustment" in payload["results"][0]


@pytest.mark.anyio
async def test_outreach_resimulation_changes_simulation_index() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/jobs/shortlist/resimulate",
            json={
                "raw_description": SAMPLE_OUTREACH_JD,
                "candidate_id": "cand_001",
                "simulation_index": 2,
            },
        )

    assert response.status_code == 200
    payload = response.json()

    assert payload["candidate"]["id"] == "cand_001"
    assert payload["conversation"]["simulation_index"] == 2
    assert len(payload["conversation"]["transcript"]) == 4


@pytest.mark.anyio
async def test_outreach_accepts_string_transcript_payload() -> None:
    parsed_job = JobDescriptionParser().parse(SAMPLE_OUTREACH_JD)
    match_result = (
        await CandidateMatcher().rank_candidates(
            parsed_job=parsed_job,
            candidates=load_candidate_fixture(),
            limit=1,
        )
    )[0]
    simulator = OutreachSimulator()

    transcript = simulator._coerce_transcript(
        [
            "Recruiter opener",
            "Candidate reply",
            "Recruiter followup",
            "Candidate followup",
        ],
        fallback=[],
    )
    interest = simulator._coerce_interest(
        llm_payload={
            "interest_score": 45,
            "interest_level": "passive",
            "positives": ["open to learning"],
            "blockers": ["missing required capabilities"],
            "summary": "Candidate is passively open.",
        },
        parsed_job=parsed_job,
        candidate_result=match_result,
    )

    assert [item.speaker for item in transcript] == [
        "recruiter",
        "candidate",
        "recruiter",
        "candidate",
    ]
    assert interest.interest_level == "medium"
