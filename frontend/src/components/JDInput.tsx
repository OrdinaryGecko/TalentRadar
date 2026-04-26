import { useState } from "react";
import { Briefcase, Sparkles } from "lucide-react";

type JDInputProps = {
  defaultValue: string;
  error: string | null;
  onSubmit: (jd: string) => void | Promise<void>;
};

export function JDInput({ defaultValue, error, onSubmit }: JDInputProps) {
  const [jd, setJd] = useState(defaultValue);

  return (
    <div className="min-h-screen bg-gradient-subtle px-6 py-16">
      <div className="mx-auto w-full max-w-2xl">
        <div className="mb-10 text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            <Sparkles className="h-3 w-3" />
            AI-powered talent scouting
          </div>
          <h1 className="mb-4 text-5xl font-bold tracking-tight md:text-6xl">
            Find your next <span className="text-gradient">great hire</span>.
          </h1>
          <p className="mx-auto max-w-xl text-lg text-muted-foreground">
            Drop in a job description. We&apos;ll surface a ranked shortlist
            with match scores, interest signals, and outreach drafts.
          </p>
        </div>

        <div className="rounded-2xl border border-border/60 bg-card p-2 shadow-card">
          <div className="flex items-center gap-2 px-4 pb-2 pt-3 text-xs text-muted-foreground">
            <Briefcase className="h-3.5 w-3.5" />
            Job Description
          </div>

          <textarea
            className="min-h-[220px] w-full resize-none border-0 bg-transparent px-4 py-2 text-base text-foreground outline-none"
            onChange={(event) => setJd(event.target.value)}
            placeholder="Paste your job description here..."
            value={jd}
          />

          <div className="flex items-center justify-between border-t border-border/60 p-3">
            <button
              className="text-xs text-muted-foreground transition hover:text-foreground"
              onClick={() => setJd(defaultValue)}
              type="button"
            >
              Try sample JD →
            </button>
            <button
              className="inline-flex items-center rounded-lg bg-gradient-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-elegant transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={jd.trim().length < 20}
              onClick={() => onSubmit(jd)}
              type="button"
            >
              <Sparkles className="mr-2 h-4 w-4" />
              Generate Shortlist
            </button>
          </div>
        </div>

        {error ? (
          <p className="mt-4 text-center text-sm text-red-600">{error}</p>
        ) : null}

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Powered by TalentRadar — local prototype
        </p>
      </div>
    </div>
  );
}
