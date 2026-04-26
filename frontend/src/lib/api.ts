import type {
  CandidateRecord,
  CandidateSeedRecord,
  ShortlistResponse,
} from "../types";

export async function buildShortlist(
  rawDescription: string,
  candidates: CandidateSeedRecord[],
): Promise<ShortlistResponse> {
  const response = await fetch("/jobs/shortlist", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      raw_description: rawDescription,
      limit: 6,
      candidates,
    })
  });

  if (!response.ok) {
    throw new Error("Unable to build shortlist.");
  }

  return (await response.json()) as ShortlistResponse;
}

export async function resimulateCandidate(
  rawDescription: string,
  candidateId: string,
  simulationIndex: number,
  candidates: CandidateSeedRecord[],
): Promise<CandidateRecord> {
  const response = await fetch("/jobs/shortlist/resimulate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      raw_description: rawDescription,
      candidate_id: candidateId,
      simulation_index: simulationIndex,
      candidates,
    })
  });

  if (!response.ok) {
    throw new Error("Unable to re-simulate outreach.");
  }

  return (await response.json()) as CandidateRecord;
}
