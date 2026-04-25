# Catalyst Backend

FastAPI service for JD parsing, candidate retrieval, scoring, and outreach simulation.

## Current API

- `GET /health`
- `GET /candidates`
- `GET /candidates/{candidate_id}`
- `POST /jobs/parse`
- `POST /jobs/match`
- `POST /jobs/outreach`
- `POST /jobs/shortlist`

## Local Commands

```bash
source .venv/bin/activate
cp .env.example .env
python -m app.seed
pytest
uvicorn app.main:app --reload
```

## Example Parse Request

```bash
curl -X POST http://127.0.0.1:8000/jobs/parse \
  -H "content-type: application/json" \
  -d '{
    "raw_description": "Senior AI Engineer\nSeniority: senior\nLocation: India\nWork mode: Remote\nRequirements:\n- 5+ years of experience\n- Python\n- FastAPI\n- LLMs\nNice to have:\n- pgvector\n- AWS"
  }'
```

## Example Match Request

```bash
curl -X POST http://127.0.0.1:8000/jobs/match \
  -H "content-type: application/json" \
  -d '{
    "raw_description": "Senior AI Engineer\nSeniority: senior\nLocation: India\nWork mode: Remote\n\nRequirements:\n- 5+ years of experience\n- Python\n- FastAPI\n- LLMs\n- pgvector\n\nNice to have:\n- AWS",
    "limit": 3
  }'
```

## Example Outreach Request

```bash
curl -X POST http://127.0.0.1:8000/jobs/outreach \
  -H "content-type: application/json" \
  -d '{
    "raw_description": "Senior AI Engineer\nSeniority: senior\nLocation: India\nWork mode: Remote\n\nRequirements:\n- 5+ years of experience\n- Python\n- FastAPI\n- LLMs\n- pgvector\n\nNice to have:\n- AWS",
    "limit": 2
  }'
```

## Example Shortlist Request

```bash
curl -X POST http://127.0.0.1:8000/jobs/shortlist \
  -H "content-type: application/json" \
  -d '{
    "raw_description": "Senior AI Engineer\nSeniority: senior\nLocation: India\nWork mode: Remote\n\nRequirements:\n- 5+ years of experience\n- Python\n- FastAPI\n- LLMs\n- pgvector\n\nNice to have:\n- AWS",
    "limit": 3
  }'
```

## Optional LLM Explanation Providers

Put these in `backend/.env` if you want explanation summaries from an external model:

```bash
LLM_PROVIDER=gemini   # or groq, openai, local
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=your-key
```

Optional:

```bash
LLM_BASE_URL=
LLM_TIMEOUT_SECONDS=20
```

If no provider is configured, the app falls back to deterministic local explanations.
