from httpx import ASGITransport, AsyncClient
import pytest

from app.jd_parser import JobDescriptionParser
from app.main import app


SAMPLE_JD = """
Senior AI Engineer
Seniority: senior
Location: India
Work mode: Remote

Requirements:
- 5+ years of experience
- Python
- FastAPI
- LLMs
- Vector databases

Nice to have:
- pgvector
- AWS
""".strip()


def test_parser_extracts_structured_requirements() -> None:
    parser = JobDescriptionParser()

    parsed = parser.parse(SAMPLE_JD)

    assert parsed.title == "Senior AI Engineer"
    assert parsed.normalized_requirement.seniority == "senior"
    assert parsed.normalized_requirement.minimum_years_experience == 5
    assert parsed.normalized_requirement.location == "India"
    assert parsed.normalized_requirement.required_capabilities == [
        "Python",
        "FastAPI",
        "LLMs",
        "Vector databases",
    ]
    assert parsed.normalized_requirement.preferred_capabilities == [
        "pgvector",
        "AWS",
    ]


@pytest.mark.anyio
async def test_parse_endpoint_returns_normalized_payload() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post("/jobs/parse", json={"raw_description": SAMPLE_JD})

    assert response.status_code == 200

    payload = response.json()

    assert payload["title"] == "Senior AI Engineer"
    assert payload["normalized_requirement"]["work_mode"] == "remote"
    assert "required_capability" in [
        signal["section"] for signal in payload["signals"]
    ]
