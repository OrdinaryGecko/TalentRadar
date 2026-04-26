export function ProcessingState() {
  return (
    <div className="min-h-screen bg-gradient-subtle px-6 py-16">
      <div className="mx-auto flex max-w-xl flex-col items-center text-center">
        <div className="relative h-20 w-20">
          <div className="absolute inset-0 rounded-full border-4 border-primary/15" />
          <div className="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-primary border-r-primary" />
          <div className="absolute inset-3 rounded-full bg-card shadow-elegant" />
        </div>
        <div className="mt-8 inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
          TalentRadar
        </div>
        <h1 className="mt-6 text-4xl font-bold tracking-tight">
          Building shortlist
        </h1>
        <p className="mt-3 max-w-md text-muted-foreground">
          Parsing the JD, scoring candidates, simulating outreach, and ranking
          the final shortlist.
        </p>
      </div>
    </div>
  );
}
