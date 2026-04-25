import json
from functools import lru_cache
from pathlib import Path

from app.models import Candidate


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CANDIDATE_FIXTURE_PATH = DATA_DIR / "candidates.json"


@lru_cache(maxsize=1)
def load_candidate_fixture() -> list[Candidate]:
    payload = json.loads(CANDIDATE_FIXTURE_PATH.read_text())

    return [Candidate.model_validate(item) for item in payload]


class CandidateRepository:
    def __init__(self) -> None:
        self._candidates = load_candidate_fixture()

    def list_candidates(self) -> list[Candidate]:
        return list(self._candidates)

    def get_candidate(self, candidate_id: str) -> Candidate | None:
        for candidate in self._candidates:
            if candidate.id == candidate_id:
                return candidate

        return None
