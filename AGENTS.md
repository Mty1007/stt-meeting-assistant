# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

Cantonese-English mixed-speech transcription + meeting minutes app.
- **Backend**: Python FastAPI (`backend/`) — run from inside `backend/` with its own `.venv`
- **Frontend**: Next.js 15 + React 19 + Tailwind (`frontend/`) — run from inside `frontend/`
- No monorepo tooling; the two directories are fully independent.

## Run Commands

```bash
# Backend (must be run from backend/)
cd backend && source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (must be run from frontend/)
cd frontend && npm run dev   # http://localhost:3000
```

No test suite exists in this project. No lint CI for the backend.

Frontend lint: `cd frontend && npm run lint`

## Critical Architecture

### Request flow (3 sequential API calls)
1. `POST /api/upload` → returns `job_id` (UUID); file saved as `uploads/<job_id>.<ext>`
2. `POST /api/transcribe` → reads uploaded file by globbing `uploads/<job_id>.*`; converts to `<job_id>.prepared.wav` (16 kHz mono); runs pyannote diarization then STT per segment
3. `POST /api/summarize` → passes raw transcript text to watsonx.ai Granite

### Next.js proxy
`next.config.ts` rewrites all `/api/*` calls to `http://127.0.0.1:8000/api/*`. Frontend code only ever calls `/api/...` (relative), never the backend port directly.

### Heavy model loading
`diarization.py` and `ibm_stt.py`/`watsonx.py` use `@lru_cache(maxsize=1)` on their client/pipeline getters — models are loaded once per process. The pyannote model (~1 GB) downloads from Hugging Face on first use; `HUGGINGFACE_TOKEN` must have accepted model terms on HF.

### IBM Watson STT model
Hard-coded to `zh-CN_CantoneseBroadbandModel` — Cantonese broadband model. Do not change unless intentionally switching language support.

### Blocking SDK calls in async context
Both IBM Watson SDK and watsonx.ai SDK are synchronous. They are wrapped via `loop.run_in_executor(None, ...)` to stay async-safe. ElevenLabs uses `httpx.AsyncClient` and fires all segments concurrently with `asyncio.gather`.

## Environment Variables

All read by `config.py` via `pydantic-settings`. Copy `backend/.env.example` → `backend/.env`.

| Variable | Required for |
|---|---|
| `IBM_STT_API_KEY` + `IBM_STT_URL` | IBM engine |
| `ELEVENLABS_API_KEY` | ElevenLabs engine |
| `WATSONX_API_KEY` + `WATSONX_PROJECT_ID` | Summarization |
| `HUGGINGFACE_TOKEN` | pyannote model download |
| `INSTANA_AGENT_KEY` | Optional monitoring |

`WATSONX_URL` defaults to `https://us-south.ml.cloud.ibm.com` — override for other regions.

## Code Style

**Backend (Python)**
- Use `structlog.get_logger()` for all logging — never `print()` or `logging.getLogger()`
- Log with keyword args: `log.info("event_name", key=value)` — not f-strings
- Pydantic v2 schemas live in `backend/models/schemas.py`; enums inherit `(str, Enum)`
- Settings accessed via `get_settings()` (cached singleton) — never `os.environ` directly
- New services go in `backend/services/`; new routes go in `backend/routers/` and must be registered in `main.py`

**Frontend (TypeScript/React)**
- `@/*` path alias maps to `frontend/src/*`
- Custom color: `bg-brand` / `text-brand` (defined in `tailwind.config.ts` as `#3b82d4`)
- All API types duplicated from backend schemas in `frontend/src/lib/api.ts` — keep them in sync
- UI text is Traditional Chinese (廣東話 / 粵語) — keep new UI strings consistent
- `strict: true` TypeScript — no implicit `any`
