import { useState } from "react";

import { Dashboard } from "./components/Dashboard";
import { JDInput } from "./components/JDInput";
import { ProcessingState } from "./components/ProcessingState";
import { buildShortlist } from "./lib/api";
import type { CandidateRecord } from "./types";

type View = "input" | "processing" | "dashboard";

const sampleJd = `Senior AI Engineer
Seniority: senior
Location: India
Work mode: Remote

Requirements:
- 5+ years of experience
- Python
- FastAPI
- LLMs
- pgvector

Nice to have:
- AWS`;

export default function App() {
  const [view, setView] = useState<View>("input");
  const [error, setError] = useState<string | null>(null);
  const [jobTitle, setJobTitle] = useState<string>("");
  const [candidates, setCandidates] = useState<CandidateRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  async function handleSubmit(jd: string) {
    setView("processing");
    setError(null);

    try {
      const shortlist = await buildShortlist(jd);
      setJobTitle(shortlist.parsed_job.normalized_requirement.role);
      setCandidates(shortlist.results);
      setSelectedId(null);
      setView("dashboard");
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Unable to build shortlist."
      );
      setView("input");
    }
  }

  if (view === "processing") {
    return <ProcessingState />;
  }

  if (view === "dashboard") {
    return (
      <Dashboard
        candidates={candidates}
        jobTitle={jobTitle}
        onReset={() => {
          setSelectedId(null);
          setCandidates([]);
          setJobTitle("");
          setView("input");
        }}
        onSelect={setSelectedId}
        selectedId={selectedId}
      />
    );
  }

  return <JDInput defaultValue={sampleJd} error={error} onSubmit={handleSubmit} />;
}
