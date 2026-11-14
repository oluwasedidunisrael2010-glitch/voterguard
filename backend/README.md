# VoterGuard backend (MVP prototype)

FastAPI + SQLite + OpenCV + pHash. Synthetic data only. Not connected to INEC or any national register.
Frontend: https://voterguard.vercel.app

## Run locally / in Codespaces
    cd backend
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python -m pytest -q          # run tests first
    uvicorn app.main:app --reload --port 8000
Open /docs for interactive API docs.

## API
| Method | Route | Purpose |
|---|---|---|
| GET | /health | service + database check |
| POST | /analyze | upload image (field `file`), run checks, save, return result |
| GET | /analyses, /analyses/{id} | saved history |
| POST | /collection | add synthetic reference image (`file`, `label`) |
| GET | /collection | list reference images |
| POST | /screen?max_distance=10 | analyze + compare with collection |
| GET | /matches | match candidates |
| PATCH | /matches/{id}/review | reviewer decision (JSON) |
| GET | /stats | real dashboard counts |
| GET | /audit | audit events |

## Deploy (Render, Docker)
New Web Service > connect repo > branch > Root Directory `backend` > Runtime Docker.
Env vars: CORS_ORIGINS=https://voterguard.vercel.app
Then in Vercel set NEXT_PUBLIC_API_URL to the Render URL and redeploy.
Free tiers sleep when idle and may reset the disk (SQLite data can be lost): demo use only.

## Status
Implemented and tested (13 automated tests): health, analysis, validation (non-image, empty, malformed,
truncated, unsupported, oversized), persistence across restart, duplicate screening, review, stats, audit, CORS.
Not implemented: authentication/roles, AI-image detection, registration rules/cases, offline sync, Tauri, INEC integration.
No authentication yet: do not expose real data.
