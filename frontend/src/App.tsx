import { FormEvent, useState } from "react";

type Signal = {
  section: string;
  value: string;
};

type ParsedJob = {
  title: string;
  normalized_requirement: {
    role: string;
    seniority: string | null;
    required_capabilities: string[];
    preferred_capabilities: string[];
    minimum_years_experience: number;
    location: string;
    work_mode: string;
  };
  signals: Signal[];
};

type TranscriptTurn = {
  speaker: string;
  message: string;
  turn_index: number;
};

type ShortlistItem = {
  candidate: {
    id: string;
    full_name: string;
    headline: string;
    current_company: string;
    current_title: string;
    location: string;
  };
  match_score: number;
  interest_score: number;
  combined_score: number;
  explanation: {
    summary: string;
    strengths: string[];
    concerns: string[];
    matched_capabilities: string[];
    missing_capabilities: string[];
    matched_preferred_capabilities: string[];
    missing_preferred_capabilities: string[];
    provider: string;
    generation_mode: string;
  };
  interest: {
    interest_level: string;
    interest_score: number;
    positives: string[];
    blockers: string[];
    summary: string;
  };
  conversation: {
    transcript: TranscriptTurn[];
  };
};

type ShortlistResponse = {
  parsed_job: ParsedJob;
  results: ShortlistItem[];
};

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

const progressItems = [
  "JD parsing",
  "candidate matching",
  "preferred-skill weighting",
  "outreach simulation",
  "interest scoring",
  "shortlist ranking"
];

export default function App() {
  const [rawDescription, setRawDescription] = useState(sampleJd);
  const [data, setData] = useState<ShortlistResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/jobs/shortlist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          raw_description: rawDescription,
          limit: 5
        })
      });

      if (!response.ok) {
        throw new Error("Unable to build shortlist.");
      }

      const payload = (await response.json()) as ShortlistResponse;
      setData(payload);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Unexpected error while building shortlist."
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">TalentRadar</p>
        <p className="tagline">Scan. Match. Engage. Hire.</p>
        <h1>Rank talent by fit and real engagement intent.</h1>
        <p className="lead">
          Paste a job description, parse it into structured requirements, score
          seeded candidate profiles, simulate outreach, and review a ranked
          shortlist ready for recruiter action.
        </p>
        <div className="progress-strip">
          {progressItems.map((item) => (
            <span className="progress-pill" key={item}>
              {item}
            </span>
          ))}
        </div>
      </section>

      <section className="workspace-grid">
        <form className="panel composer-panel" onSubmit={handleSubmit}>
          <div className="section-head">
            <div>
              <p className="kicker">Step 1</p>
              <h2>Job Description Input</h2>
            </div>
            <span className="status-badge">{isLoading ? "running" : "ready"}</span>
          </div>
          <label className="field-label" htmlFor="jd-input">
            Paste job description
          </label>
          <textarea
            className="jd-input"
            id="jd-input"
            value={rawDescription}
            onChange={(event) => setRawDescription(event.target.value)}
          />
          <div className="composer-actions">
            <button className="primary-button" disabled={isLoading} type="submit">
              {isLoading ? "Building shortlist..." : "Build shortlist"}
            </button>
            <p className="helper-text">
              Uses local candidate data, explainable scoring, and simulated
              outreach.
            </p>
          </div>
          {error ? <p className="error-text">{error}</p> : null}
        </form>

        <section className="panel parsed-panel">
          <div className="section-head">
            <div>
              <p className="kicker">Step 2</p>
              <h2>Parsed Requirements</h2>
            </div>
          </div>

          {data ? (
            <>
              <div className="metrics-grid">
                <article className="metric-card">
                  <span className="metric-label">Role</span>
                  <strong>{data.parsed_job.normalized_requirement.role}</strong>
                </article>
                <article className="metric-card">
                  <span className="metric-label">Experience</span>
                  <strong>
                    {data.parsed_job.normalized_requirement.minimum_years_experience}+ years
                  </strong>
                </article>
                <article className="metric-card">
                  <span className="metric-label">Work mode</span>
                  <strong>{data.parsed_job.normalized_requirement.work_mode}</strong>
                </article>
                <article className="metric-card">
                  <span className="metric-label">Location</span>
                  <strong>{data.parsed_job.normalized_requirement.location}</strong>
                </article>
              </div>

              <div className="chip-group">
                {data.parsed_job.normalized_requirement.required_capabilities.map(
                  (capability) => (
                    <span className="chip chip-required" key={capability}>
                      {capability}
                    </span>
                  )
                )}
                {data.parsed_job.normalized_requirement.preferred_capabilities.map(
                  (capability) => (
                    <span className="chip chip-preferred" key={capability}>
                      {capability}
                    </span>
                  )
                )}
              </div>

              <div className="signal-list">
                {data.parsed_job.signals.map((signal, index) => (
                  <div className="signal-row" key={`${signal.section}-${index}`}>
                    <span>{signal.section}</span>
                    <strong>{signal.value}</strong>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <p className="empty-state">
              Structured parsing will appear here after you build the shortlist.
            </p>
          )}
        </section>
      </section>

      <section className="panel results-panel">
        <div className="section-head">
          <div>
            <p className="kicker">Step 3</p>
            <h2>Ranked Shortlist</h2>
          </div>
          {data ? (
            <span className="status-badge">{data.results.length} candidates</span>
          ) : null}
        </div>

        {data ? (
          <div className="candidate-stack">
            {data.results.map((item, index) => (
              <article className="candidate-card" key={item.candidate.id}>
                <div className="candidate-header">
                  <div>
                    <p className="rank-chip">#{index + 1}</p>
                    <h3>{item.candidate.full_name}</h3>
                    <p className="candidate-meta">
                      {item.candidate.current_title} at {item.candidate.current_company}
                    </p>
                    <p className="candidate-headline">{item.candidate.headline}</p>
                  </div>
                  <div className="score-grid">
                    <div>
                      <span>match</span>
                      <strong>{item.match_score}</strong>
                    </div>
                    <div>
                      <span>interest</span>
                      <strong>{item.interest_score}</strong>
                    </div>
                    <div className="score-accent">
                      <span>combined</span>
                      <strong>{item.combined_score}</strong>
                    </div>
                  </div>
                </div>

                <div className="candidate-columns">
                  <section>
                    <h4>Why matched</h4>
                    <p className="summary-text">{item.explanation.summary}</p>
                    <ul className="detail-list">
                      {item.explanation.strengths.map((strength) => (
                        <li key={strength}>{strength}</li>
                      ))}
                    </ul>
                    {item.explanation.concerns.length > 0 ? (
                      <>
                        <h4>Watch-outs</h4>
                        <ul className="detail-list muted-list">
                          {item.explanation.concerns.map((concern) => (
                            <li key={concern}>{concern}</li>
                          ))}
                        </ul>
                      </>
                    ) : null}
                  </section>

                  <section>
                    <h4>Interest read</h4>
                    <p className="summary-text">{item.interest.summary}</p>
                    <ul className="detail-list">
                      {item.interest.positives.map((positive) => (
                        <li key={positive}>{positive}</li>
                      ))}
                    </ul>
                    {item.interest.blockers.length > 0 ? (
                      <>
                        <h4>Possible blockers</h4>
                        <ul className="detail-list muted-list">
                          {item.interest.blockers.map((blocker) => (
                            <li key={blocker}>{blocker}</li>
                          ))}
                        </ul>
                      </>
                    ) : null}
                  </section>

                  <section>
                    <h4>Conversation snapshot</h4>
                    <div className="transcript">
                      {item.conversation.transcript.map((turn) => (
                        <div
                          className={`transcript-turn transcript-${turn.speaker}`}
                          key={`${item.candidate.id}-${turn.turn_index}`}
                        >
                          <span>{turn.speaker}</span>
                          <p>{turn.message}</p>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-state">
            No shortlist yet. Submit a JD to generate ranked candidates with
            match and interest scores.
          </p>
        )}
      </section>
    </main>
  );
}
