from fastapi import FastAPI, HTTPException

from app.jd_parser import JobDescriptionParser
from app.models import JobParseRequest, JobParseResponse
from app.repository import CandidateRepository

app = FastAPI(
    title="Catalyst API",
    description="Backend API for the talent scouting and engagement agent",
    version="0.1.0",
)

candidate_repository = CandidateRepository()
job_description_parser = JobDescriptionParser()


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/candidates")
async def list_candidates() -> dict[str, object]:
    candidates = candidate_repository.list_candidates()

    return {
        "count": len(candidates),
        "items": [candidate.model_dump() for candidate in candidates],
    }


@app.get("/candidates/{candidate_id}")
async def get_candidate(candidate_id: str) -> dict[str, object]:
    candidate = candidate_repository.get_candidate(candidate_id)

    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return candidate.model_dump()


@app.post("/jobs/parse", response_model=JobParseResponse)
async def parse_job_description(payload: JobParseRequest) -> JobParseResponse:
    return job_description_parser.parse(payload.raw_description)
