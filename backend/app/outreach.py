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
    def run(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
    ) -> tuple[Conversation, InterestAssessment]:
        candidate = candidate_result.candidate
        conversation = Conversation(
            job_id=parsed_job.title,
            candidate_id=candidate.id,
            transcript=[
                ConversationTurn(
                    speaker="recruiter",
                    turn_index=0,
                    message=self._recruiter_opening(
                        parsed_job=parsed_job,
                        candidate_result=candidate_result,
                    ),
                ),
                ConversationTurn(
                    speaker="candidate",
                    turn_index=1,
                    message=self._candidate_reply(
                        parsed_job=parsed_job,
                        candidate=candidate,
                    ),
                ),
                ConversationTurn(
                    speaker="recruiter",
                    turn_index=2,
                    message=self._recruiter_followup(parsed_job=parsed_job),
                ),
                ConversationTurn(
                    speaker="candidate",
                    turn_index=3,
                    message=self._candidate_followup(candidate=candidate),
                ),
            ],
        )

        return conversation, self._interest_assessment(
            parsed_job=parsed_job,
            candidate_result=candidate_result,
        )

    def _recruiter_opening(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
    ) -> str:
        role = parsed_job.normalized_requirement.role
        matched = ", ".join(candidate_result.explanation.matched_capabilities[:3])

        return (
            f"Hi {candidate_result.candidate.full_name.split()[0]}, "
            f"I'm reaching out about a {role} opening. "
            f"Your background in {matched or candidate_result.candidate.current_title} "
            f"looks relevant. Would you be open to a quick conversation?"
        )

    def _candidate_reply(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate: Candidate,
    ) -> str:
        role = parsed_job.normalized_requirement.role

        if candidate.persona == CandidatePersona.ACTIVELY_LOOKING:
            return (
                f"Yes, I'm actively exploring roles and {role} sounds relevant. "
                "Please share more details on scope and team."
            )

        if candidate.persona == CandidatePersona.PASSIVELY_OPEN:
            return (
                f"I'm not urgently looking, but I'm open to hearing more if the {role} "
                "role is hands-on and the problem space is strong."
            )

        if candidate.persona == CandidatePersona.COMPENSATION_SENSITIVE:
            return (
                "Potentially interested, but compensation range will matter a lot before "
                "I spend time on the process."
            )

        if candidate.persona == CandidatePersona.LOCATION_CONSTRAINED:
            return (
                "I could explore it if the working model fits my current location "
                "constraints. I am not open to broad relocation."
            )

        return (
            "I appreciate the message, but I am not actively available for a move right now."
        )

    def _recruiter_followup(self, *, parsed_job: JobParseResponse) -> str:
        requirement = parsed_job.normalized_requirement

        return (
            f"The role is {requirement.work_mode.value} and based in {requirement.location}. "
            f"We're looking for someone with around {requirement.minimum_years_experience}+ "
            "years who can move fairly quickly if there is mutual interest. "
            "How does that line up for you?"
        )

    def _candidate_followup(self, *, candidate: Candidate) -> str:
        if candidate.persona == CandidatePersona.ACTIVELY_LOOKING:
            return (
                f"That works for me. I can start interviewing now and my availability is about "
                f"{candidate.availability_days} days."
            )

        if candidate.persona == CandidatePersona.PASSIVELY_OPEN:
            return (
                f"That mostly lines up. I would need the role to be compelling, and my realistic "
                f"timeline would be around {candidate.availability_days} days."
            )

        if candidate.persona == CandidatePersona.COMPENSATION_SENSITIVE:
            return (
                f"I'd need the package to make sense, and my likely transition window is "
                f"{candidate.availability_days} days."
            )

        if candidate.persona == CandidatePersona.LOCATION_CONSTRAINED:
            return (
                f"If the work setup stays compatible with my location needs, I could consider it. "
                f"My timeline would be around {candidate.availability_days} days."
            )

        return (
            f"I would not plan a move in the near term. Even if I reconsider later, it would be "
            f"closer to {candidate.availability_days} days."
        )

    def _interest_assessment(
        self,
        *,
        parsed_job: JobParseResponse,
        candidate_result: CandidateMatchResult,
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

        if (
            parsed_job.normalized_requirement.work_mode
            in candidate.work_mode_preferences
        ):
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

        final_score = round(min(score, 100.0), 1)

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
