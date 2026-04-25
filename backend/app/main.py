from fastapi import FastAPI, HTTPException

from app.jd_parser import JobDescriptionParser
from app.matcher import CandidateMatcher
from app.models import (
    JobParseRequest,
    JobParseResponse,
    MatchRequest,
    MatchResponse,
    OutreachRequest,
    OutreachResponse,
    OutreachResult,
)
from app.outreach import OutreachSimulator
from app.repository import CandidateRepository

app = FastAPI(
    title="Catalyst API",
    description="Backend API for the talent scouting and engagement agent",
    version="0.1.0",
)

candidate_repository = CandidateRepository()
job_description_parser = JobDescriptionParser()
candidate_matcher = CandidateMatcher()
outreach_simulator = OutreachSimulator()


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


@app.post("/jobs/match", response_model=MatchResponse)
async def match_candidates(payload: MatchRequest) -> MatchResponse:
    parsed_job = job_description_parser.parse(payload.raw_description)
    results = await candidate_matcher.rank_candidates(
        parsed_job=parsed_job,
        candidates=candidate_repository.list_candidates(),
        limit=payload.limit,
    )

    return MatchResponse(parsed_job=parsed_job, results=results)


@app.post("/jobs/outreach", response_model=OutreachResponse)
async def run_outreach(payload: OutreachRequest) -> OutreachResponse:
    parsed_job = job_description_parser.parse(payload.raw_description)
    matched_results = await candidate_matcher.rank_candidates(
        parsed_job=parsed_job,
        candidates=candidate_repository.list_candidates(),
        limit=max(payload.limit, len(payload.candidate_ids) or payload.limit),
    )

    if payload.candidate_ids:
        selected_ids = set(payload.candidate_ids)
        matched_results = [
            result for result in matched_results if result.candidate.id in selected_ids
        ]
    else:
        matched_results = matched_results[: payload.limit]

    outreach_results: list[OutreachResult] = []

    for result in matched_results:
        conversation, interest = outreach_simulator.run(
            parsed_job=parsed_job,
            candidate_result=result,
        )
        outreach_results.append(
            OutreachResult(
                candidate=result.candidate,
                match_score=result.match_score,
                explanation=result.explanation,
                conversation=conversation,
                interest=interest,
            )
        )

    return OutreachResponse(parsed_job=parsed_job, results=outreach_results)
