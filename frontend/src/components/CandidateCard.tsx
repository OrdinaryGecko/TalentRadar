import type { CandidateRecord } from "../types";
import { candidateTags } from "../lib/tags";
import { ScoreBar } from "./ScoreBar";

type CandidateCardProps = {
  candidate: CandidateRecord;
  rank: number;
  selected: boolean;
  onSelect: () => void;
};

export function CandidateCard({
  candidate,
  rank,
  selected,
  onSelect
}: CandidateCardProps) {
  const initials = candidate.candidate.full_name
    .split(" ")
    .map((item) => item[0])
    .join("");

  const visibleSkills = candidateTags(candidate, 5);

  return (
    <article
      className={`cursor-pointer rounded-2xl border bg-card p-6 transition hover:shadow-card ${
        selected ? "border-primary/40" : "border-border/60"
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start gap-4">
        <div className="flex shrink-0 flex-col items-center gap-2">
          <div className="tabular-nums text-xs font-bold text-muted-foreground">
            #{rank}
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-primary font-semibold text-primary-foreground shadow-elegant">
            {initials}
          </div>
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <h3 className="truncate font-semibold text-foreground">
                {candidate.candidate.full_name}
              </h3>
              <p className="truncate text-sm text-muted-foreground">
                {candidate.candidate.current_title} @ {candidate.candidate.current_company}
              </p>
            </div>
            <div className="shrink-0 text-right">
              <div className="text-2xl font-bold leading-none tabular-nums text-gradient">
                {Math.round(candidate.combined_score)}
              </div>
              <div className="mt-1 text-[10px] uppercase tracking-wider text-muted-foreground">
                Combined
              </div>
            </div>
          </div>

          <div className="mt-3 flex flex-wrap gap-1.5">
            {visibleSkills.map((skill) => (
              <span
                className="rounded-full bg-secondary px-2 py-1 text-xs text-secondary-foreground"
                key={skill}
              >
                {skill}
              </span>
            ))}
          </div>

          <div className="mt-4 grid grid-cols-2 gap-4">
            <ScoreBar label="Match" size="sm" value={candidate.match_score} variant="match" />
            <ScoreBar
              label="Interest"
              size="sm"
              value={candidate.interest_score}
              variant="interest"
            />
          </div>
        </div>
      </div>

    </article>
  );
}
