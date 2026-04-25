# TalentRadar Architecture

## End-to-End Flow

```text
Recruiter JD
   ->
JD Parser
   ->
Structured Requirements
   ->
Candidate Matcher
   ->
Match Explanations
   ->
Outreach Simulator
   ->
Interest Assessment
   ->
Shortlist Ranker
   ->
Recruiter Dashboard
```

## Component Breakdown

### 1. JD Parser

File:
- `backend/app/jd_parser.py`

Responsibility:
- convert raw JD text into structured requirements
- preserve required and preferred capability phrases as generic text
- avoid hardcoded skill synonym lists in parser logic

Output:
- role
- seniority if explicitly labeled
- minimum years of experience
- location
- work mode
- required capability phrases
- preferred capability phrases
- parsing `signals`

### 2. Candidate Repository

Files:
- `backend/app/repository.py`
- `backend/data/candidates.json`

Responsibility:
- load seeded candidate profiles for the local prototype
- expose profile data to the matcher and outreach steps

Candidate data includes:
- profile summary
- title and company
- skills
- domain experience
- work mode preferences
- candidate persona
- availability window
- compensation expectation

### 3. Candidate Matcher

File:
- `backend/app/matcher.py`

Responsibility:
- compute fit between parsed JD and each candidate
- produce deterministic evidence for why a candidate fits or does not fit

Current scoring weights:

- required capability match: `40%`
- preferred capability match: `10%`
- experience fit: `20%`
- work mode alignment: `10%`
- location alignment: `10%`
- title alignment: `10%`

Outputs:
- `match_score`
- evidence-backed `MatchExplanation`

### 4. Explanation Layer

Files:
- `backend/app/explanations.py`
- `backend/app/llm.py`

Responsibility:
- keep deterministic evidence in code
- optionally refine explanation summaries using an external LLM

Provider strategy:
- `LLM_PROVIDER=local` uses deterministic local summaries
- `LLM_PROVIDER=gemini`, `groq`, or `openai` enables provider-specific generation
- provider selection is configured through `backend/.env`

Design principle:
- LLM explains the score
- code decides the score

### 5. Outreach Simulator

File:
- `backend/app/outreach.py`

Responsibility:
- simulate a short recruiter-candidate exchange
- use candidate persona and match evidence to create a 4-turn transcript

Current state:
- deterministic and rule-based
- not yet LLM-driven

Transcript structure:
- recruiter opening
- candidate reply
- recruiter follow-up
- candidate follow-up

### 6. Interest Assessment

File:
- `backend/app/outreach.py`

Responsibility:
- translate candidate persona and conversation alignment into an `interest_score`

Current factors:
- persona openness
- availability
- work mode alignment
- role-fit strength
- blockers such as compensation sensitivity or location constraints

Outputs:
- `interest_score`
- `interest_level`
- `positives`
- `blockers`
- `summary`

### 7. Shortlist Ranker

File:
- `backend/app/shortlist.py`

Responsibility:
- combine fit and intent into the final recruiter-facing ranking

Formula:

```text
combined_score = 0.65 * match_score + 0.35 * interest_score
```

Output:
- ranked shortlist entries with:
  - candidate
  - match score
  - interest score
  - combined score
  - explanation
  - interest assessment
  - transcript

### 8. Recruiter Dashboard

Files:
- `frontend/src/App.tsx`
- `frontend/src/styles.css`

Responsibility:
- provide a local UI for the whole flow
- let a recruiter paste a JD and inspect:
  - parsed requirements
  - ranked shortlist
  - score breakdown
  - conversation snapshot

## Why The System Is Structured This Way

The design intentionally separates:

- parsing
- matching
- explanation
- outreach
- interest scoring
- ranking

This makes it easier to:

- debug bad results
- swap deterministic logic for model-assisted logic later
- keep scores auditable
- evolve from local seed data to a real talent source

## Current Limitations

- candidate pool is local seeded data, not a live ATS or external search source
- JD parsing is structural, not full LLM extraction
- matching is deterministic lexical overlap, not embedding-based retrieval
- outreach is simulated, not real candidate messaging
- no persistence layer beyond local fixture loading
- no deployment config yet

## Recommended Next Evolution

1. Replace candidate retrieval with hybrid retrieval:
   structured filters + embeddings
2. Add LLM-based JD extraction on top of the current parser contract
3. Add LLM-based outreach simulation with deterministic fallback
4. Add database persistence and export
5. Add architecture diagram image for the final submission
