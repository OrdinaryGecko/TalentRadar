import json

from app.llm import LLMClient
from app.models import Candidate, JobParseResponse, MatchExplanation


class MatchExplanationService:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def finalize_explanation(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate: Candidate,
        explanation: MatchExplanation,
        match_score: float,
    ) -> MatchExplanation:
        if not self.llm_client.is_enabled():
            return explanation.model_copy(
                update={
                    "summary": self._build_local_summary(
                        candidate=candidate,
                        explanation=explanation,
                        match_score=match_score,
                    ),
                    "provider": "local",
                    "generation_mode": "deterministic",
                }
            )

        try:
            llm_response = await self.llm_client.generate_json(
                system_prompt=self._system_prompt(),
                user_prompt=self._user_prompt(
                    parsed_job=parsed_job,
                    candidate=candidate,
                    explanation=explanation,
                    match_score=match_score,
                ),
            )
        except Exception:
            llm_response = None

        if not llm_response:
            return explanation.model_copy(
                update={
                    "summary": self._build_local_summary(
                        candidate=candidate,
                        explanation=explanation,
                        match_score=match_score,
                    ),
                    "provider": "local",
                    "generation_mode": "fallback",
                }
            )

        return explanation.model_copy(
            update={
                "summary": str(llm_response.get("summary", "")).strip()
                or self._build_local_summary(
                    candidate=candidate,
                    explanation=explanation,
                    match_score=match_score,
                ),
                "strengths": self._coerce_list(
                    llm_response.get("strengths"),
                    explanation.strengths,
                ),
                "concerns": self._coerce_list(
                    llm_response.get("concerns"),
                    explanation.concerns,
                ),
                "provider": self.llm_client.settings.provider.lower(),
                "generation_mode": "llm",
            }
        )

    def _system_prompt(self) -> str:
        return (
            "You generate concise recruiting match explanations. "
            "Return strict JSON with keys: summary, strengths, concerns. "
            "Do not invent facts beyond the provided evidence."
        )

    def _user_prompt(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate: Candidate,
        explanation: MatchExplanation,
        match_score: float,
    ) -> str:
        payload = {
            "job": parsed_job.model_dump(),
            "candidate": {
                "full_name": candidate.full_name,
                "headline": candidate.headline,
                "current_title": candidate.current_title,
                "skills": candidate.skills,
                "domain_experience": candidate.domain_experience,
                "summary": candidate.summary,
            },
            "score": match_score,
            "evidence": explanation.model_dump(),
        }

        return json.dumps(payload, indent=2)

    def _build_local_summary(
        self,
        *,
        candidate: Candidate,
        explanation: MatchExplanation,
        match_score: float,
    ) -> str:
        summary = (
            f"{candidate.full_name} scores {match_score:.1f} based on "
            f"{len(explanation.matched_capabilities)} required capability matches"
        )

        if explanation.matched_preferred_capabilities:
            summary += (
                f" and {len(explanation.matched_preferred_capabilities)} preferred matches"
            )

        if explanation.missing_capabilities:
            summary += f"; main gaps are {', '.join(explanation.missing_capabilities)}"

        elif explanation.missing_preferred_capabilities:
            summary += (
                "; required capabilities are covered, with preferred gaps in "
                + ", ".join(explanation.missing_preferred_capabilities)
            )

        else:
            summary += "; the profile aligns cleanly on both required and preferred areas"

        return summary

    def _coerce_list(
        self,
        value: object,
        fallback: list[str],
    ) -> list[str]:
        if isinstance(value, list):
            normalized = [str(item).strip() for item in value if str(item).strip()]

            if normalized:
                return normalized

        return fallback
