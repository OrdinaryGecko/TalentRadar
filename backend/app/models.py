from enum import Enum

from pydantic import BaseModel, Field


class WorkMode(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class CandidateStatus(str, Enum):
    ACTIVE = "active"
    PASSIVE = "passive"
    UNAVAILABLE = "unavailable"


class CandidatePersona(str, Enum):
    ACTIVELY_LOOKING = "actively_looking"
    PASSIVELY_OPEN = "passively_open"
    COMPENSATION_SENSITIVE = "compensation_sensitive"
    LOCATION_CONSTRAINED = "location_constrained"
    CURRENTLY_UNAVAILABLE = "currently_unavailable"


class JobRequirement(BaseModel):
    role: str
    seniority: str | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    preferred_capabilities: list[str] = Field(default_factory=list)
    minimum_years_experience: int
    location: str
    work_mode: WorkMode


class JobParseRequest(BaseModel):
    raw_description: str = Field(min_length=20)


class MatchRequest(BaseModel):
    raw_description: str = Field(min_length=20)
    limit: int = Field(default=5, ge=1, le=20)


class JobParseSignal(BaseModel):
    section: str
    value: str


class JobParseResponse(BaseModel):
    title: str
    normalized_requirement: JobRequirement
    signals: list[JobParseSignal] = Field(default_factory=list)


class Job(BaseModel):
    id: str
    title: str
    raw_description: str
    requirements: JobRequirement


class Candidate(BaseModel):
    id: str
    full_name: str
    headline: str
    location: str
    work_mode_preferences: list[WorkMode] = Field(default_factory=list)
    years_experience: int
    current_title: str
    current_company: str
    skills: list[str] = Field(default_factory=list)
    domain_experience: list[str] = Field(default_factory=list)
    summary: str
    persona: CandidatePersona
    availability_days: int
    compensation_expectation_lpa: int
    engagement_status: CandidateStatus


class MatchExplanation(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    matched_capabilities: list[str] = Field(default_factory=list)
    missing_capabilities: list[str] = Field(default_factory=list)
    matched_preferred_capabilities: list[str] = Field(default_factory=list)
    missing_preferred_capabilities: list[str] = Field(default_factory=list)
    provider: str = "local"
    generation_mode: str = "deterministic"


class CandidateMatch(BaseModel):
    job_id: str
    candidate_id: str
    match_score: float
    explanation: MatchExplanation


class CandidateMatchResult(BaseModel):
    candidate: Candidate
    match_score: float
    explanation: MatchExplanation


class MatchResponse(BaseModel):
    parsed_job: JobParseResponse
    results: list[CandidateMatchResult] = Field(default_factory=list)


class InterestAssessment(BaseModel):
    interest_score: float
    interest_level: str
    positives: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    summary: str


class OutreachRequest(BaseModel):
    raw_description: str = Field(min_length=20)
    candidate_ids: list[str] = Field(default_factory=list)
    limit: int = Field(default=3, ge=1, le=10)


class OutreachResult(BaseModel):
    candidate: Candidate
    match_score: float
    explanation: MatchExplanation
    conversation: Conversation | None = None
    interest: InterestAssessment | None = None


class OutreachResponse(BaseModel):
    parsed_job: JobParseResponse
    results: list[OutreachResult] = Field(default_factory=list)


class ConversationTurn(BaseModel):
    speaker: str
    message: str
    turn_index: int


class Conversation(BaseModel):
    job_id: str
    candidate_id: str
    transcript: list[ConversationTurn] = Field(default_factory=list)


class ShortlistEntry(BaseModel):
    job_id: str
    candidate_id: str
    match_score: float
    interest_score: float
    combined_score: float
