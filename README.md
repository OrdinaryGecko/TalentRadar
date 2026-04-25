# Catalyst

AI-powered talent scouting and engagement agent prototype.

## Stack

- Frontend: React + Vite + TypeScript
- Backend: FastAPI + Python

## Project Structure

- `frontend/` React application
- `backend/` FastAPI service
- `docs/` architecture and supporting documents

## Local Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Current Status

Project scaffold is in place. Matching, scoring, and outreach flows are not implemented yet.
