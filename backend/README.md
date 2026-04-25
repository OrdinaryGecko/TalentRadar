# Catalyst Backend

FastAPI service for JD parsing, candidate retrieval, scoring, and outreach simulation.

## Current API

- `GET /health`
- `GET /candidates`
- `GET /candidates/{candidate_id}`
- `POST /jobs/parse`

## Local Commands

```bash
source .venv/bin/activate
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
