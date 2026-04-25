import re
from dataclasses import dataclass

from app.explanations import MatchExplanationService
from app.models import (
    Candidate,
    CandidateMatchResult,
    JobParseResponse,
    MatchExplanation,
)


@dataclass(frozen=True)
class MatchWeights:
    required_capability: float = 0.4
    preferred_capability: float = 0.1
    experience: float = 0.2
    work_mode: float = 0.1
    location: float = 0.1
    title_alignment: float = 0.1


class CandidateMatcher:
    def __init__(
        self,
        weights: MatchWeights | None = None,
        explanation_service: MatchExplanationService | None = None,
    ) -> None:
        self.weights = weights or MatchWeights()
        self.explanation_service = explanation_service or MatchExplanationService()

    async def rank_candidates(
        self,
        parsed_job: JobParseResponse,
        candidates: list[Candidate],
        limit: int = 5,
    ) -> list[CandidateMatchResult]:
        results: list[CandidateMatchResult] = []

        for candidate in candidates:
            results.append(
                await self._score_candidate(parsed_job=parsed_job, candidate=candidate)
            )

        results.sort(key=lambda item: item.match_score, reverse=True)

        return results[:limit]

    async def _score_candidate(
        self,
        parsed_job: JobParseResponse,
        candidate: Candidate,
    ) -> CandidateMatchResult:
        requirement = parsed_job.normalized_requirement
        matched_capabilities, missing_capabilities = self._capability_overlap(
            requirement.required_capabilities,
            candidate,
        )
        matched_preferred_capabilities, missing_preferred_capabilities = (
            self._capability_overlap(
                requirement.preferred_capabilities,
                candidate,
            )
        )

        required_capability_score = self._capability_score(
            requirement.required_capabilities,
            matched_capabilities,
        )
        preferred_capability_score = self._capability_score(
            requirement.preferred_capabilities,
            matched_preferred_capabilities,
        )
        experience_score = self._experience_score(
            requirement.minimum_years_experience,
            candidate.years_experience,
        )
        work_mode_score = self._work_mode_score(requirement.work_mode.value, candidate)
        location_score = self._location_score(requirement.location, candidate.location)
        title_alignment_score = self._title_alignment_score(requirement.role, candidate)

        total_score = round(
            (
                required_capability_score * self.weights.required_capability
                + preferred_capability_score * self.weights.preferred_capability
                + experience_score * self.weights.experience
                + work_mode_score * self.weights.work_mode
                + location_score * self.weights.location
                + title_alignment_score * self.weights.title_alignment
            )
            * 100,
            1,
        )

        base_explanation = self._build_explanation(
            candidate=candidate,
            matched_capabilities=matched_capabilities,
            missing_capabilities=missing_capabilities,
            matched_preferred_capabilities=matched_preferred_capabilities,
            missing_preferred_capabilities=missing_preferred_capabilities,
            required_capability_score=required_capability_score,
            preferred_capability_score=preferred_capability_score,
            experience_score=experience_score,
            work_mode_score=work_mode_score,
            location_score=location_score,
        )
        explanation = await self.explanation_service.finalize_explanation(
            parsed_job=parsed_job,
            candidate=candidate,
            explanation=base_explanation,
            match_score=total_score,
        )

        return CandidateMatchResult(
            candidate=candidate,
            match_score=total_score,
            explanation=explanation,
        )

    def _capability_overlap(
        self,
        required_capabilities: list[str],
        candidate: Candidate,
    ) -> tuple[list[str], list[str]]:
        candidate_terms = self._candidate_terms(candidate)
        matched: list[str] = []
        missing: list[str] = []

        for capability in required_capabilities:
            normalized_requirement = self._normalize(capability)

            if normalized_requirement in candidate_terms:
                matched.append(capability)
            else:
                missing.append(capability)

        return matched, missing

    def _candidate_terms(self, candidate: Candidate) -> set[str]:
        values = [
            *candidate.skills,
            *candidate.domain_experience,
            candidate.current_title,
            candidate.headline,
            candidate.summary,
        ]
        normalized_terms: set[str] = set()

        for value in values:
            normalized_value = self._normalize(value)

            if normalized_value:
                normalized_terms.add(normalized_value)

            for phrase in self._split_into_phrases(value):
                normalized_phrase = self._normalize(phrase)

                if normalized_phrase:
                    normalized_terms.add(normalized_phrase)

        return normalized_terms

    def _split_into_phrases(self, value: str) -> list[str]:
        tokens = re.split(r"[,/]| and |\.", value, flags=re.IGNORECASE)

        return [token.strip() for token in tokens if token.strip()]

    def _normalize(self, value: str) -> str:
        lowered = value.lower().strip()
        lowered = re.sub(r"[^a-z0-9\+\#\s]", " ", lowered)
        lowered = re.sub(r"\s+", " ", lowered)

        return lowered

    def _capability_score(
        self,
        required_capabilities: list[str],
        matched_capabilities: list[str],
    ) -> float:
        if not required_capabilities:
            return 1.0

        return len(matched_capabilities) / len(required_capabilities)

    def _experience_score(
        self,
        minimum_years_experience: int,
        candidate_years_experience: int,
    ) -> float:
        if minimum_years_experience <= 0:
            return 1.0

        return min(candidate_years_experience / minimum_years_experience, 1.0)

    def _work_mode_score(self, required_work_mode: str, candidate: Candidate) -> float:
        candidate_modes = {mode.value for mode in candidate.work_mode_preferences}

        if required_work_mode in candidate_modes:
            return 1.0

        if required_work_mode == "remote" and "hybrid" in candidate_modes:
            return 0.5

        return 0.0

    def _location_score(self, required_location: str, candidate_location: str) -> float:
        normalized_required = self._normalize(required_location)
        normalized_candidate = self._normalize(candidate_location)

        if normalized_required in {"", "unspecified"}:
            return 1.0

        if normalized_required in normalized_candidate:
            return 1.0

        return 0.0

    def _title_alignment_score(self, role: str, candidate: Candidate) -> float:
        role_tokens = set(self._normalize(role).split())
        title_tokens = set(self._normalize(candidate.current_title).split())

        if not role_tokens:
            return 0.0

        return len(role_tokens & title_tokens) / len(role_tokens)

    def _build_explanation(
        self,
        candidate: Candidate,
        matched_capabilities: list[str],
        missing_capabilities: list[str],
        matched_preferred_capabilities: list[str],
        missing_preferred_capabilities: list[str],
        required_capability_score: float,
        preferred_capability_score: float,
        experience_score: float,
        work_mode_score: float,
        location_score: float,
    ) -> MatchExplanation:
        strengths: list[str] = []
        concerns: list[str] = []

        if matched_capabilities:
            strengths.append(
                f"Matches {len(matched_capabilities)} required capabilities: "
                + ", ".join(matched_capabilities)
            )

        if required_capability_score == 1.0:
            strengths.append("Covers all required capability phrases from the JD")

        if matched_preferred_capabilities:
            strengths.append(
                f"Also matches preferred capabilities: "
                + ", ".join(matched_preferred_capabilities)
            )

        if experience_score == 1.0:
            strengths.append(
                f"Meets the experience requirement with {candidate.years_experience} years"
            )
        else:
            concerns.append(
                f"Below the requested experience range at {candidate.years_experience} years"
            )

        if work_mode_score == 1.0:
            strengths.append("Work mode preference aligns with the job")
        elif work_mode_score == 0.5:
            concerns.append("Work mode is only partially aligned via hybrid preference")
        else:
            concerns.append("Work mode preference does not align cleanly")

        if location_score == 1.0:
            strengths.append("Location constraint is satisfied")
        else:
            concerns.append("Location constraint may need recruiter review")

        if missing_capabilities:
            concerns.append(
                "Missing explicit evidence for: " + ", ".join(missing_capabilities)
            )

        if preferred_capability_score < 1.0 and missing_preferred_capabilities:
            concerns.append(
                "Preferred capability gaps: "
                + ", ".join(missing_preferred_capabilities)
            )

        return MatchExplanation(
            summary="",
            strengths=strengths,
            concerns=concerns,
            matched_capabilities=matched_capabilities,
            missing_capabilities=missing_capabilities,
            matched_preferred_capabilities=matched_preferred_capabilities,
            missing_preferred_capabilities=missing_preferred_capabilities,
        )
