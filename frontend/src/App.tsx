const roadmapItems = [
  "Parse a job description into structured requirements",
  "Retrieve matching candidates from a seeded talent pool",
  "Score each candidate with explainable match logic",
  "Simulate recruiter outreach and candidate responses",
  "Rank the final shortlist using match and interest scores"
];

export default function App() {
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Catalyst</p>
        <h1>AI-powered talent scouting and engagement agent</h1>
        <p className="lead">
          Local prototype scaffold for JD parsing, candidate matching, outreach
          simulation, and recruiter-ready ranking.
        </p>
      </section>

      <section className="panel">
        <h2>Implementation Roadmap</h2>
        <ul className="roadmap">
          {roadmapItems.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    </main>
  );
}
