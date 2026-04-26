from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

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
    ShortlistEntry,
    ShortlistRequest,
    ShortlistResimulateRequest,
    ShortlistResponse,
)
from app.outreach import OutreachSimulator
from app.repository import CandidateRepository
from app.shortlist import ShortlistRanker

app = FastAPI(
    title="TalentRadar API",
    description="Backend API for the talent scouting and engagement agent",
    version="0.1.0",
)

candidate_repository = CandidateRepository()
job_description_parser = JobDescriptionParser()
candidate_matcher = CandidateMatcher()
outreach_simulator = OutreachSimulator()
shortlist_ranker = ShortlistRanker()
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def resolve_candidates(custom_candidates: list | None = None):
    if custom_candidates:
        return custom_candidates

    return candidate_repository.list_candidates()


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
        candidates=resolve_candidates(payload.candidates),
        limit=payload.limit,
    )

    return MatchResponse(parsed_job=parsed_job, results=results)


@app.post("/jobs/outreach", response_model=OutreachResponse)
async def run_outreach(payload: OutreachRequest) -> OutreachResponse:
    parsed_job = job_description_parser.parse(payload.raw_description)
    candidate_pool = resolve_candidates(payload.candidates)
    matched_results = await candidate_matcher.rank_candidates(
        parsed_job=parsed_job,
        candidates=candidate_pool,
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
        conversation, interest, adjusted_match_score = await outreach_simulator.run(
            parsed_job=parsed_job,
            candidate_result=result,
        )
        outreach_results.append(
            OutreachResult(
                candidate=result.candidate,
                base_match_score=result.match_score,
                match_score=adjusted_match_score,
                match_adjustment=round(adjusted_match_score - result.match_score, 1),
                explanation=result.explanation,
                conversation=conversation,
                interest=interest,
            )
        )

    return OutreachResponse(parsed_job=parsed_job, results=outreach_results)


@app.post("/jobs/shortlist", response_model=ShortlistResponse)
async def build_shortlist(payload: ShortlistRequest) -> ShortlistResponse:
    outreach_response = await run_outreach(
        OutreachRequest(
            raw_description=payload.raw_description,
            limit=payload.limit,
            candidate_ids=[],
            candidates=payload.candidates,
        )
    )
    shortlist = shortlist_ranker.rank(outreach_response.results)

    return ShortlistResponse(
        parsed_job=outreach_response.parsed_job,
        results=shortlist,
    )


@app.post("/jobs/shortlist/resimulate", response_model=ShortlistEntry)
async def resimulate_shortlist_entry(
    payload: ShortlistResimulateRequest,
) -> ShortlistEntry:
    parsed_job = job_description_parser.parse(payload.raw_description)
    candidate_pool = resolve_candidates(payload.candidates)
    candidate = next(
        (item for item in candidate_pool if item.id == payload.candidate_id),
        None,
    )

    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    match_result = await candidate_matcher.score_candidate(
        parsed_job=parsed_job,
        candidate=candidate,
    )
    conversation, interest, adjusted_match_score = await outreach_simulator.run(
        parsed_job=parsed_job,
        candidate_result=match_result,
        simulation_index=payload.simulation_index,
    )
    outreach_result = OutreachResult(
        candidate=match_result.candidate,
        base_match_score=match_result.match_score,
        match_score=adjusted_match_score,
        match_adjustment=round(adjusted_match_score - match_result.match_score, 1),
        explanation=match_result.explanation,
        conversation=conversation,
        interest=interest,
    )

    return shortlist_ranker.to_shortlist_entry(outreach_result)


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
