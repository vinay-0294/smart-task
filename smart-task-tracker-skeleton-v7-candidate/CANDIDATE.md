# 📄 Candidate Handout — Smart Task Tracker (Barebones Scaffold)

## Goal
Implement the core features of a small task tracker in **~4 hours** using:
- **Frontend:** Next.js (TypeScript)
- **Backend:** FastAPI (Python)
- **Data:** Your choice (SQLite recommended), DB-agnostic design
- **AI:** Implement a **FAKE** Smart Intake adapter that suggests (title, priority)

## What's provided
- Docker + Compose
- Next.js app with a minimal page
- FastAPI app with **stub routes** that return **501 Not Implemented**
- A working `/healthz` endpoint
- `.env.example` and basic scaffolding

## Your tasks (core scope)
1. **Projects & Tasks API** (FastAPI): implement the stubbed routes
   - `GET/POST /api/projects`
   - `GET/POST /api/projects/{id}/tasks?status=...`
   - `PATCH /api/tasks/{id}`
2. **Smart Intake**: `POST /api/ai/intake` — implement a deterministic FAKE adapter returning `{ title, priority }`.
3. **UI** (Next.js): build a simple list + form
   - Render tasks and **filter by status**
   - Create tasks with `title` + `priority`
   - Provide a Smart Intake interaction (paste text → prefill form)
4. **Tests**: Back-end tests (**≥2**): one happy path + one error path
5. **Docs**: Short README notes (run steps, design choices, TODOs) + **AI Usage Report**

## Time cap
Spend **no more than 4 hours**. If you run out of time, document trade-offs and TODOs.

## Running the app
Start both frontend and backend together:
```bash
docker compose up --build
```

## Submission
- Share a Git repo or zip with code and Docker setup
- Include `.env.example` and clear run instructions