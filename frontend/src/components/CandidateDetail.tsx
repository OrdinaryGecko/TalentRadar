import type { ReactNode } from "react";
import { Heart, MessageSquare, RefreshCw, Sparkles, X } from "lucide-react";

import { candidateTags } from "../lib/tags";
import type { CandidateRecord } from "../types";
import { ScoreBar } from "./ScoreBar";

type CandidateDetailProps = {
  candidate: CandidateRecord | null;
  isResimulating: boolean;
  onClose: () => void;
  onResimulate: (candidateId: string, simulationIndex: number) => Promise<void>;
};

export function CandidateDetail({
  candidate,
  isResimulating,
  onClose,
  onResimulate
}: CandidateDetailProps) {
  if (!candidate) {
    return null;
  }

  const initials = candidate.candidate.full_name
    .split(" ")
    .map((item) => item[0])
    .join("");
  const visibleSkills = candidateTags(candidate);

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-card shadow-card"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
      >
        <div className="relative overflow-hidden rounded-t-2xl bg-gradient-hero p-8 text-primary-foreground">
          <button
            className="absolute right-4 top-4 z-10 rounded-full bg-white/15 p-2 text-primary-foreground transition hover:bg-white/25"
            onClick={onClose}
            type="button"
          >
            <X className="h-4 w-4" />
          </button>

          <div className="flex items-start gap-5">
            <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/20 bg-white/15 text-2xl font-bold backdrop-blur">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="text-2xl font-semibold">
                {candidate.candidate.full_name}
              </h2>
              <p className="mt-1 text-primary-foreground/80">
                {candidate.candidate.current_title} @ {candidate.candidate.current_company}
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {visibleSkills.map((skill) => (
                  <span
                    className="rounded-full bg-white/15 px-2.5 py-1 text-xs font-normal text-primary-foreground"
                    key={skill}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            <div className="shrink-0 pr-14 text-right">
              <div className="text-4xl font-bold leading-none tabular-nums">
                {Math.round(candidate.combined_score)}
              </div>
              <div className="mt-1 text-xs uppercase tracking-wider text-primary-foreground/70">
                Combined
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-8 p-8">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <ScoreBar label="Match Score" value={candidate.match_score} variant="match" />
            <ScoreBar
              label="Interest Score"
              value={candidate.interest_score}
              variant="interest"
            />
          </div>

          <ExplanationBlock
            icon={<Sparkles className="h-4 w-4" />}
            label="Why they match"
            text={candidate.explanation.summary}
            tone="match"
          />

          <ExplanationBlock
            icon={<Heart className="h-4 w-4" />}
            label="Why they're (un)interested"
            text={candidate.interest.summary}
            tone="interest"
          />

          <div>
            <div className="mb-4 flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
              <h4 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Simulated Outreach
              </h4>
              </div>
              <button
                className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-xs font-medium text-foreground transition hover:bg-secondary disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isResimulating}
                onClick={() =>
                  onResimulate(
                    candidate.candidate.id,
                    candidate.conversation.simulation_index + 1
                  )
                }
                type="button"
              >
                <RefreshCw
                  className={`h-3.5 w-3.5 ${isResimulating ? "animate-spin" : ""}`}
                />
                Re-simulate
              </button>
            </div>
            <div className="space-y-3">
              {candidate.conversation.transcript.map((message) => (
                <div
                  className={`flex ${
                    message.speaker === "recruiter" ? "justify-start" : "justify-end"
                  }`}
                  key={`${message.speaker}-${message.turn_index}`}
                >
                  <div
                    className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm ${
                      message.speaker === "recruiter"
                        ? "rounded-bl-sm bg-secondary text-secondary-foreground"
                        : "rounded-br-sm bg-gradient-primary text-primary-foreground"
                    }`}
                  >
                    <div className="mb-0.5 text-[10px] uppercase tracking-wider opacity-60">
                      {message.speaker}
                    </div>
                    {message.message}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ExplanationBlock({
  icon,
  label,
  text,
  tone
}: {
  icon: ReactNode;
  label: string;
  text: string;
  tone: "match" | "interest";
}) {
  return (
    <div>
      <div
        className={`mb-2 flex items-center gap-2 text-sm font-semibold ${
          tone === "match" ? "text-primary" : "text-foreground"
        }`}
      >
        {icon}
        <span className="text-xs uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-sm leading-relaxed text-foreground/80">{text}</p>
    </div>
  );
}
