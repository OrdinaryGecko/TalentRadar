import json

from app.llm import LLMClient
from app.models import (
    Candidate,
    CandidateMatchResult,
    CandidatePersona,
    Conversation,
    ConversationTurn,
    InterestAssessment,
    JobParseResponse,
)


class OutreachSimulator:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    async def run(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int = 0,
    ) -> tuple[Conversation, InterestAssessment, float]:
        if self.llm_client.is_enabled():
            llm_payload = await self._llm_payload(
                parsed_job=parsed_job,
                candidate_result=candidate_result,
                simulation_index=simulation_index,
            )

            if llm_payload is not None:
                transcript = self._coerce_transcript(
                    llm_payload.get("transcript"),
                    fallback=self._fallback_transcript(
                        parsed_job=parsed_job,
                        candidate_result=candidate_result,
                        simulation_index=simulation_index,
                    ),
                )
                interest = self._coerce_interest(
                    llm_payload=llm_payload,
                    parsed_job=parsed_job,
                    candidate_result=candidate_result,
                )
                match_adjustment = self._coerce_match_adjustment(
                    llm_payload.get("match_adjustment")
                )

                return (
                    Conversation(
                        job_id=parsed_job.title,
                        candidate_id=candidate_result.candidate.id,
                        simulation_index=simulation_index,
                        provider=self.llm_client.settings.provider.lower(),
                        generation_mode="llm",
                        transcript=transcript,
                    ),
                    interest,
                    self._adjust_match_score(
                        candidate_result.match_score,
                        match_adjustment,
                    ),
                )

        fallback_conversation, fallback_interest, match_adjustment = self._fallback_result(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
            simulation_index=simulation_index,
        )

        return (
            fallback_conversation,
            fallback_interest,
            self._adjust_match_score(candidate_result.match_score, match_adjustment),
        )

    async def _llm_payload(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int,
    ) -> dict[str, object] | None:
        try:
            return await self.llm_client.generate_json(
                system_prompt=self._system_prompt(),
                user_prompt=self._user_prompt(
                    parsed_job=parsed_job,
                    candidate_result=candidate_result,
                    simulation_index=simulation_index,
                ),
                temperature=0.8,
            )
        except Exception:
            return None

    def _system_prompt(self) -> str:
        return (
            "You simulate short recruiter outreach for a recruiting workflow. "
            "Return strict JSON only. "
            "The transcript must contain exactly 4 messages alternating recruiter, candidate, recruiter, candidate. "
            "Use concise, realistic professional language. "
            "Also score candidate interest and a small post-conversation match adjustment. "
            "JSON keys: transcript, interest_score, interest_level, positives, blockers, summary, match_adjustment. "
            "match_adjustment must be a number between -8 and 5. "
            "Do not invent factual background beyond the provided candidate profile."
        )

    def _user_prompt(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int,
    ) -> str:
        candidate = candidate_result.candidate
        payload = {
            "simulation_index": simulation_index,
            "variation_instruction": (
                "This is a fresh re-simulation attempt. Vary wording and emphasis from prior attempts while staying consistent with the profile."
            ),
            "job": parsed_job.model_dump(),
            "candidate": {
                "full_name": candidate.full_name,
                "headline": candidate.headline,
                "current_title": candidate.current_title,
                "current_company": candidate.current_company,
                "location": candidate.location,
                "skills": candidate.skills,
                "domain_experience": candidate.domain_experience,
                "persona": candidate.persona.value,
                "availability_days": candidate.availability_days,
                "work_mode_preferences": [
                    mode.value for mode in candidate.work_mode_preferences
                ],
                "summary": candidate.summary,
            },
            "match_context": {
                "base_match_score": candidate_result.match_score,
                "matched_capabilities": candidate_result.explanation.matched_capabilities,
                "missing_capabilities": candidate_result.explanation.missing_capabilities,
                "matched_preferred_capabilities": candidate_result.explanation.matched_preferred_capabilities,
                "missing_preferred_capabilities": candidate_result.explanation.missing_preferred_capabilities,
            },
        }

        return json.dumps(payload, indent=2)

    def _coerce_transcript(
        self,
        value: object,
        *,
        fallback: list[ConversationTurn],
    ) -> list[ConversationTurn]:
        if not isinstance(value, list) or len(value) != 4:
            return fallback

        expected_speakers = ["recruiter", "candidate", "recruiter", "candidate"]
        transcript: list[ConversationTurn] = []

        for index, speaker in enumerate(expected_speakers):
            item = value[index]

            if not isinstance(item, dict):
                return fallback

            message = str(item.get("message", "")).strip()
            item_speaker = str(item.get("speaker", "")).strip().lower()

            if not message or item_speaker != speaker:
                return fallback

            transcript.append(
                ConversationTurn(
                    speaker=speaker,
                    turn_index=index,
                    message=message,
                )
            )

        return transcript

    def _coerce_interest(
        self,
        *,
        llm_payload: dict[str, object],
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
    ) -> InterestAssessment:
        fallback = self._fallback_interest(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
            simulation_index=0,
        )
        raw_score = llm_payload.get("interest_score")

        try:
            interest_score = float(raw_score)
        except (TypeError, ValueError):
            interest_score = fallback.interest_score

        interest_score = round(max(0.0, min(100.0, interest_score)), 1)
        raw_level = str(llm_payload.get("interest_level", "")).strip().lower()

        if raw_level not in {"high", "medium", "low"}:
            if interest_score >= 75:
                raw_level = "high"
            elif interest_score >= 50:
                raw_level = "medium"
            else:
                raw_level = "low"

        positives = self._coerce_list(
            llm_payload.get("positives"),
            fallback.positives,
        )
        blockers = self._coerce_list(
            llm_payload.get("blockers"),
            fallback.blockers,
        )
        summary = str(llm_payload.get("summary", "")).strip() or fallback.summary

        return InterestAssessment(
            interest_score=interest_score,
            interest_level=raw_level,
            positives=positives,
            blockers=blockers,
            summary=summary,
        )

    def _coerce_match_adjustment(self, value: object) -> float:
        try:
            adjustment = float(value)
        except (TypeError, ValueError):
            return 0.0

        return round(max(-8.0, min(5.0, adjustment)), 1)

    def _adjust_match_score(self, base_match_score: float, adjustment: float) -> float:
        return round(max(0.0, min(100.0, base_match_score + adjustment)), 1)

    def _fallback_result(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int,
    ) -> tuple[Conversation, InterestAssessment, float]:
        transcript = self._fallback_transcript(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
            simulation_index=simulation_index,
        )
        interest = self._fallback_interest(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
            simulation_index=simulation_index,
        )
        match_adjustment = self._fallback_match_adjustment(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
            interest=interest,
        )

        return (
            Conversation(
                job_id=parsed_job.title,
                candidate_id=candidate_result.candidate.id,
                simulation_index=simulation_index,
                provider="local",
                generation_mode="deterministic",
                transcript=transcript,
            ),
            interest,
            match_adjustment,
        )

    def _fallback_transcript(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int,
    ) -> list[ConversationTurn]:
        candidate = candidate_result.candidate
        variants = simulation_index % 3
        openings = [
            (
                f"Hi {candidate.full_name.split()[0]}, I'm reaching out about a "
                f"{parsed_job.normalized_requirement.role} opening. "
                f"Your work on {self._top_match_phrase(candidate_result)} looks relevant. "
                "Would you be open to a quick conversation?"
            ),
            (
                f"Hi {candidate.full_name.split()[0]}, we are hiring for a "
                f"{parsed_job.normalized_requirement.role} role and your background in "
                f"{self._top_match_phrase(candidate_result)} stood out. "
                "Would you be open to hearing more?"
            ),
            (
                f"Hi {candidate.full_name.split()[0]}, I'm working on a search for a "
                f"{parsed_job.normalized_requirement.role}. "
                f"You seem aligned on {self._top_match_phrase(candidate_result)}. "
                "Interested in a quick intro?"
            ),
        ]
        recruiter_followups = [
            (
                f"The role is {parsed_job.normalized_requirement.work_mode.value} and based in "
                f"{parsed_job.normalized_requirement.location}. "
                f"We're targeting around {parsed_job.normalized_requirement.minimum_years_experience}+ "
                "years of experience. How does that line up for you?"
            ),
            (
                f"It is a {parsed_job.normalized_requirement.work_mode.value} role in "
                f"{parsed_job.normalized_requirement.location}, with a strong backend AI scope. "
                "Would timing and working model fit your current situation?"
            ),
            (
                f"The role has a fairly hands-on scope and we'd want someone comfortable moving "
                f"within roughly {parsed_job.normalized_requirement.minimum_years_experience}+ years seniority expectations. "
                "Would that be workable for you?"
            ),
        ]

        return [
            ConversationTurn(
                speaker="recruiter",
                turn_index=0,
                message=openings[variants],
            ),
            ConversationTurn(
                speaker="candidate",
                turn_index=1,
                message=self._candidate_reply(candidate=candidate, role=parsed_job.normalized_requirement.role, variant=variants),
            ),
            ConversationTurn(
                speaker="recruiter",
                turn_index=2,
                message=recruiter_followups[variants],
            ),
            ConversationTurn(
                speaker="candidate",
                turn_index=3,
                message=self._candidate_followup(candidate=candidate, variant=variants),
            ),
        ]

    def _fallback_interest(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        simulation_index: int,
    ) -> InterestAssessment:
        candidate = candidate_result.candidate
        positives: list[str] = []
        blockers: list[str] = []
        score = 0.0

        persona_bonus = {
            CandidatePersona.ACTIVELY_LOOKING: 45.0,
            CandidatePersona.PASSIVELY_OPEN: 30.0,
            CandidatePersona.COMPENSATION_SENSITIVE: 24.0,
            CandidatePersona.LOCATION_CONSTRAINED: 18.0,
            CandidatePersona.CURRENTLY_UNAVAILABLE: 8.0,
        }
        score += persona_bonus[candidate.persona]

        if candidate.availability_days <= 30:
            positives.append("Available within 30 days")
            score += 20.0
        elif candidate.availability_days <= 45:
            positives.append("Reasonable transition window")
            score += 12.0
        else:
            blockers.append("Longer availability timeline")
            score += 4.0

        if parsed_job.normalized_requirement.work_mode in candidate.work_mode_preferences:
            positives.append("Work mode aligns with current preference")
            score += 15.0
        else:
            blockers.append("Work mode fit may require negotiation")

        if candidate_result.match_score >= 80:
            positives.append("High role-fit makes outreach easier to convert")
            score += 10.0
        elif candidate_result.match_score < 60:
            blockers.append("Lower fit may reduce candidate conviction")

        if candidate.persona == CandidatePersona.COMPENSATION_SENSITIVE:
            blockers.append("Compensation needs to be confirmed early")

        if candidate.persona == CandidatePersona.LOCATION_CONSTRAINED:
            blockers.append("Location flexibility is limited")

        if candidate.persona == CandidatePersona.CURRENTLY_UNAVAILABLE:
            blockers.append("Candidate is not actively open right now")

        score += [-2.0, 0.0, 2.0][simulation_index % 3]
        final_score = round(min(max(score, 0.0), 100.0), 1)

        if final_score >= 75:
            level = "high"
        elif final_score >= 50:
            level = "medium"
        else:
            level = "low"

        summary = (
            f"{candidate.full_name} shows {level} interest based on persona, "
            f"availability, and response alignment. Interest score is {final_score:.1f}."
        )

        return InterestAssessment(
            interest_score=final_score,
            interest_level=level,
            positives=positives,
            blockers=blockers,
            summary=summary,
        )

    def _fallback_match_adjustment(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
        interest: InterestAssessment,
    ) -> float:
        adjustment = 0.0
        candidate = candidate_result.candidate

        if candidate_result.explanation.matched_preferred_capabilities:
            adjustment += 1.5

        if parsed_job.normalized_requirement.work_mode not in candidate.work_mode_preferences:
            adjustment -= 2.0

        if interest.interest_score >= 80:
            adjustment += 1.0
        elif interest.interest_score < 45:
            adjustment -= 1.5

        return round(max(-4.0, min(3.0, adjustment)), 1)

    def _candidate_reply(self, *, candidate: Candidate, role: str, variant: int) -> str:
        responses = {
            CandidatePersona.ACTIVELY_LOOKING: [
                f"Yes, I'm actively exploring and {role} sounds relevant. Please share the scope and team details.",
                f"Definitely open. {role} is close to what I'm targeting right now, so happy to learn more.",
                f"Yes, I am in the market and this sounds like a good fit on the surface. Can you share more context?",
            ],
            CandidatePersona.PASSIVELY_OPEN: [
                f"I'm not actively looking, but I'm open if the {role} role is hands-on and the problem space is strong.",
                f"Potentially open. I would want the role to be substantive, but I'm willing to hear more.",
                f"I'm selective, though the role sounds relevant enough for a quick conversation.",
            ],
            CandidatePersona.COMPENSATION_SENSITIVE: [
                "Potentially interested, but compensation range will matter a lot before I spend time on the process.",
                "Open in principle, though I would want to understand compensation early.",
                "Maybe, but I would only proceed if the package and level are well aligned.",
            ],
            CandidatePersona.LOCATION_CONSTRAINED: [
                "I could explore it if the working model fits my current location constraints. I am not open to broad relocation.",
                "I'm open only if the work setup stays compatible with my current location needs.",
                "Possibly, but location flexibility is limited on my side, so that would need to line up.",
            ],
            CandidatePersona.CURRENTLY_UNAVAILABLE: [
                "I appreciate the message, but I am not actively available for a move right now.",
                "Thanks for reaching out. I'm not in a place to change roles immediately.",
                "I appreciate the note, though I'm not really available to switch in the near term.",
            ],
        }

        return responses[candidate.persona][variant]

    def _candidate_followup(self, *, candidate: Candidate, variant: int) -> str:
        responses = {
            CandidatePersona.ACTIVELY_LOOKING: [
                f"That works for me. I can start interviewing now and my availability is about {candidate.availability_days} days.",
                f"Yes, that lines up well. I could start conversations now and would likely need around {candidate.availability_days} days.",
                f"That seems workable. I can engage soon, with a transition window of roughly {candidate.availability_days} days.",
            ],
            CandidatePersona.PASSIVELY_OPEN: [
                f"That mostly lines up. I would need the role to be compelling, and my realistic timeline would be around {candidate.availability_days} days.",
                f"Broadly yes, assuming the role is strong enough. My timing would be around {candidate.availability_days} days.",
                f"It could work, although I'd be selective. My likely transition window is about {candidate.availability_days} days.",
            ],
            CandidatePersona.COMPENSATION_SENSITIVE: [
                f"I'd need the package to make sense, and my likely transition window is {candidate.availability_days} days.",
                f"If the compensation aligns, the timing is manageable. I would need around {candidate.availability_days} days.",
                f"The timeline is workable at roughly {candidate.availability_days} days, but I would want compensation clarity early.",
            ],
            CandidatePersona.LOCATION_CONSTRAINED: [
                f"If the work setup stays compatible with my location needs, I could consider it. My timeline would be around {candidate.availability_days} days.",
                f"If the role stays compatible with my location constraints, the timing could work in about {candidate.availability_days} days.",
                f"Potentially yes, provided the setup fits my location needs. I would likely need {candidate.availability_days} days.",
            ],
            CandidatePersona.CURRENTLY_UNAVAILABLE: [
                f"I would not plan a move in the near term. Even if I reconsider later, it would be closer to {candidate.availability_days} days.",
                f"I do not expect to move soon. If that changes, the timeline would still be more like {candidate.availability_days} days.",
                f"Not realistically right now. If circumstances changed, I would still be looking at something like {candidate.availability_days} days.",
            ],
        }

        return responses[candidate.persona][variant]

    def _top_match_phrase(self, candidate_result: CandidateMatchResult) -> str:
        if candidate_result.explanation.matched_capabilities:
            return ", ".join(candidate_result.explanation.matched_capabilities[:2])

        return candidate_result.candidate.current_title

    def _coerce_list(self, value: object, fallback: list[str]) -> list[str]:
        if isinstance(value, list):
            normalized = [str(item).strip() for item in value if str(item).strip()]

            if normalized:
                return normalized

        return fallback
