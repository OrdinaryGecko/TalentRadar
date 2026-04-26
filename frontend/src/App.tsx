import { useState } from "react";

import { Dashboard } from "./components/Dashboard";
import { JDInput } from "./components/JDInput";
import { ProcessingState } from "./components/ProcessingState";
import { buildShortlist, resimulateCandidate } from "./lib/api";
import type { CandidateRecord, CandidateSeedRecord } from "./types";

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
  const [activeJd, setActiveJd] = useState<string>(sampleJd);
  const [jobTitle, setJobTitle] = useState<string>("");
  const [candidates, setCandidates] = useState<CandidateRecord[]>([]);
  const [candidatePool, setCandidatePool] = useState<CandidateSeedRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [resimulatingId, setResimulatingId] = useState<string | null>(null);

  async function handleSubmit(jd: string) {
    setView("processing");
    setError(null);

    try {
      const shortlist = await buildShortlist(jd, candidatePool);
      setActiveJd(jd);
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

  async function handleResimulate(candidateId: string, simulationIndex: number) {
    setResimulatingId(candidateId);

    try {
      const refreshed = await resimulateCandidate(
        activeJd,
        candidateId,
        simulationIndex,
        candidatePool,
      );
      setCandidates((current) =>
        current.map((candidate) =>
          candidate.candidate.id === candidateId ? refreshed : candidate
        )
      );
    } finally {
      setResimulatingId(null);
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
          setActiveJd(sampleJd);
          setCandidatePool([]);
          setResimulatingId(null);
          setView("input");
        }}
        onResimulate={handleResimulate}
        onSelect={setSelectedId}
        resimulatingId={resimulatingId}
        selectedId={selectedId}
      />
    );
  }

  return (
    <JDInput
      candidates={candidatePool}
      defaultValue=""
      error={error}
      onCandidatesChange={setCandidatePool}
      sampleValue={sampleJd}
      onSubmit={handleSubmit}
    />
  );
}
