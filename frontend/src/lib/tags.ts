import type { CandidateRecord } from "../types";

function normalizeTag(value: string): string {
  return value.trim().toLowerCase();
}

export function candidateTags(
  candidate: CandidateRecord,
  limit?: number
): string[] {
  const ordered = [
    ...candidate.explanation.matched_capabilities,
    ...candidate.explanation.matched_preferred_capabilities
  ];

  if (ordered.length === 0) {
    ordered.push(...(candidate.candidate.skills ?? []).slice(0, 5));
  }

  const seen = new Set<string>();
  const unique = ordered.filter((tag) => {
    const normalized = normalizeTag(tag);

    if (!normalized || seen.has(normalized)) {
      return false;
    }

    seen.add(normalized);
    return true;
  });

  return typeof limit === "number" ? unique.slice(0, limit) : unique;
}
