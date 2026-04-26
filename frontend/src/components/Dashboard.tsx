import { useMemo, useState } from "react";
import { ArrowLeft, TrendingUp, Users } from "lucide-react";

import type { CandidateRecord } from "../types";
import { CandidateCard } from "./CandidateCard";
import { CandidateDetail } from "./CandidateDetail";

type DashboardProps = {
  candidates: CandidateRecord[];
  jobTitle: string;
  onReset: () => void;
  onResimulate: (candidateId: string, simulationIndex: number) => Promise<void>;
  onSelect: (candidateId: string | null) => void;
  resimulatingId: string | null;
  selectedId: string | null;
};

type SortKey = "combined_score" | "match_score" | "interest_score";

const sorts: { key: SortKey; label: string }[] = [
  { key: "combined_score", label: "Combined" },
  { key: "match_score", label: "Match" },
  { key: "interest_score", label: "Interest" }
];

export function Dashboard({
  candidates,
  jobTitle,
  onReset,
  onResimulate,
  onSelect,
  resimulatingId,
  selectedId
}: DashboardProps) {
  const [sortKey, setSortKey] = useState<SortKey>("combined_score");

  const sortedCandidates = useMemo(
    () => [...candidates].sort((left, right) => right[sortKey] - left[sortKey]),
    [candidates, sortKey]
  );

  const selectedCandidate =
    sortedCandidates.find((candidate) => candidate.candidate.id === selectedId) ?? null;

  const averageCombined = Math.round(
    sortedCandidates.reduce((sum, candidate) => sum + candidate.combined_score, 0) /
      Math.max(sortedCandidates.length, 1)
  );

  return (
    <div className="min-h-screen bg-gradient-subtle">
      <header className="sticky top-0 z-20 border-b border-border/60 bg-card/80 backdrop-blur">
        <div className="container flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              className="inline-flex items-center gap-2 rounded-md px-2.5 py-1.5 text-sm text-muted-foreground transition hover:bg-secondary hover:text-foreground"
              onClick={onReset}
              type="button"
            >
              <ArrowLeft className="h-4 w-4" />
              New search
            </button>
            <div className="h-5 w-px bg-border" />
            <div>
              <h1 className="font-semibold">Shortlist</h1>
              <p className="text-xs text-muted-foreground">{jobTitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span className="tabular-nums">{sortedCandidates.length} candidates</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              <span>
                Avg combined{" "}
                <span className="font-semibold text-foreground tabular-nums">
                  {averageCombined}%
                </span>
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="container px-6 py-8">
        <section>
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Top candidates</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Ranked by {sorts.find((sort) => sort.key === sortKey)?.label.toLowerCase()} score
              </p>
            </div>
            <div className="inline-flex items-center gap-1 rounded-lg bg-secondary p-1">
              {sorts.map((sort) => (
                <button
                  className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
                    sort.key === sortKey
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  key={sort.key}
                  onClick={() => setSortKey(sort.key)}
                  type="button"
                >
                  {sort.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {sortedCandidates.map((candidate, index) => (
              <CandidateCard
                candidate={candidate}
                key={candidate.candidate.id}
                onSelect={() => onSelect(candidate.candidate.id)}
                rank={index + 1}
                selected={candidate.candidate.id === selectedId}
              />
            ))}
          </div>
        </section>
      </main>

      <CandidateDetail
        candidate={selectedCandidate}
        isResimulating={
          selectedCandidate?.candidate.id != null &&
          resimulatingId === selectedCandidate.candidate.id
        }
        onClose={() => onSelect(null)}
        onResimulate={onResimulate}
      />
    </div>
  );
}
