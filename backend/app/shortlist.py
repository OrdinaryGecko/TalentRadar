from app.models import (
    InterestAssessment,
    MatchExplanation,
    OutreachResult,
    ShortlistEntry,
)


class ShortlistRanker:
    def __init__(
        self,
        *,
        match_weight: float = 0.65,
        interest_weight: float = 0.35,
    ) -> None:
        self.match_weight = match_weight
        self.interest_weight = interest_weight

    def rank(self, outreach_results: list[OutreachResult]) -> list[ShortlistEntry]:
        ranked = [
            self._to_shortlist_entry(result)
            for result in outreach_results
            if result.interest and result.conversation
        ]
        ranked.sort(key=lambda item: item.combined_score, reverse=True)

        return ranked

    def _to_shortlist_entry(self, result: OutreachResult) -> ShortlistEntry:
        interest = result.interest or InterestAssessment(
            interest_score=0,
            interest_level="low",
            positives=[],
            blockers=["Interest assessment missing"],
            summary="Interest assessment missing.",
        )
        conversation = result.conversation

        if conversation is None:
            raise ValueError("Conversation is required for shortlist ranking")

        return ShortlistEntry(
            candidate=result.candidate,
            match_score=result.match_score,
            interest_score=interest.interest_score,
            combined_score=round(
                result.match_score * self.match_weight
                + interest.interest_score * self.interest_weight,
                1,
            ),
            explanation=result.explanation,
            interest=interest,
            conversation=conversation,
        )
