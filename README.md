# TalentRadar

Scan. Match. Engage. Hire.

TalentRadar takes a job description, parses it into structured requirements, matches it against a seeded candidate pool, simulates recruiter outreach, scores candidate interest, and produces a ranked shortlist with explainable `match_score` and `interest_score`.

## What It Covers

- JD parsing into structured hiring requirements
- candidate matching with explainable scoring
- simulated recruiter outreach
- interest scoring from the simulated conversation
- final shortlist ranking using fit plus intent
- local recruiter dashboard built with React + Vite

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + Python
- LLM integration: provider-based config with `local`, `gemini`, `groq`, or `openai`
- Data layer: seeded local JSON dataset for candidate profiles

## Project Structure

- `frontend/` recruiter dashboard
- `backend/` FastAPI service and matching logic
- `docs/` architecture, sample outputs, and demo notes

## Local Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173` and proxies API calls to the backend on `http://127.0.0.1:8000`.

## LLM Configuration

TalentRadar supports provider-based explanation generation. Put these in `backend/.env`:

```bash
LLM_PROVIDER=local
LLM_MODEL=
LLM_API_KEY=
LLM_BASE_URL=
LLM_TIMEOUT_SECONDS=20
```

Supported `LLM_PROVIDER` values:

- `local`
- `gemini`
- `groq`
- `openai`

If `LLM_PROVIDER=local`, explanation summaries stay deterministic and offline-safe.

## API Summary

- `GET /health`
- `GET /candidates`
- `GET /candidates/{candidate_id}`
- `POST /jobs/parse`
- `POST /jobs/match`
- `POST /jobs/outreach`
- `POST /jobs/shortlist`

## Scoring Logic

### Match Score

Current weighted scoring:

- required capability match: `40%`
- preferred capability match: `10%`
- experience fit: `20%`
- work mode alignment: `10%`
- location alignment: `10%`
- title alignment: `10%`

The backend returns explanation evidence including:

- matched required capabilities
- missing required capabilities
- matched preferred capabilities
- missing preferred capabilities
- strengths
- concerns

### Interest Score

Current interest scoring uses the simulated conversation plus candidate persona:

- persona openness
- availability window
- work mode alignment
- overall role-fit strength
- blockers such as compensation sensitivity or location constraints

Interest output includes:

- `interest_score`
- `interest_level`
- `positives`
- `blockers`
- `summary`

### Final Shortlist Ranking

Combined ranking formula:

```text
combined_score = 0.65 * match_score + 0.35 * interest_score
```

## Sample Input

```text
Senior AI Engineer
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
- AWS
```

## Sample Output

Sample shortlist result for the above input:

1. `Aditi Rao`
   `match_score: 90.0`
   `interest_score: 75.0`
   `combined_score: 84.8`
2. `Rahul Menon`
   `match_score: 73.3`
   `interest_score: 80.0`
   `combined_score: 75.6`
3. `Arjun Nair`
   `match_score: 63.3`
   `interest_score: 51.0`
   `combined_score: 59.0`

Detailed sample output is documented in [docs/sample-output.md](/home/sumit/Programming/deccanai/catalyst/docs/sample-output.md).

## How To Demo

Suggested demo flow:

1. open the React dashboard
2. paste the sample JD
3. submit and show the parsed requirements panel
4. highlight shortlist ranking and explanation summaries
5. open the conversation snapshot for top candidates
6. explain why a high-fit but missing-preferred-skill candidate still ranks strongly
7. explain why a lower-fit but more interested candidate can move upward

Detailed talking points are in [docs/demo-script.md](/home/sumit/Programming/deccanai/catalyst/docs/demo-script.md).

## Architecture

See [docs/architecture.md](/home/sumit/Programming/deccanai/catalyst/docs/architecture.md) for:

- system flow
- component responsibilities
- scoring breakdown
- current limitations and extension path

## Verification

Backend:

```bash
cd backend
source .venv/bin/activate
pytest
```

Frontend:

```bash
cd frontend
npm run build
```

## Current Status

Implemented:

- local candidate seed data
- generic structural JD parsing
- explainable match scoring
- provider-based explanation generation
- deterministic outreach simulation
- interest scoring
- shortlist ranking
- recruiter dashboard workflow

Still pending for a full submission package:

- deployed URL
- recorded demo video
- exported architecture diagram asset
- optional CSV/export flow
