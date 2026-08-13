# Coding Rules (Non-Obvious)

## Backend

- **Never use `os.environ` directly** — always `get_settings()` from `config.py` (lru_cache singleton).
- **Never use `print()` or stdlib `logging`** — use `structlog.get_logger()` with event-name + keyword args: `log.info("event_name", key=value)`.
- **Blocking SDK calls must use `run_in_executor`** — IBM Watson and watsonx.ai SDKs are synchronous; wrap them with `loop.run_in_executor(None, ...)`. ElevenLabs is async (`httpx.AsyncClient`).
- **New routers must be registered in `main.py`** — `app.include_router(...)` with `prefix="/api"`.
- **Audio pipeline requires 16 kHz mono WAV** — always pass the result of `prepare_audio()` (not the raw upload) to diarization and STT functions.
- **Diarization skips segments < 0.5 s** — do not expect sub-half-second speech in output.
- **`COST_PER_MINUTE_USD`** is defined per-service in `ibm_stt.py` and `elevenlabs_stt.py`; update there if pricing changes.

## Frontend

- **All API calls go through `/api/...` relative paths** — do not hardcode the backend port; `next.config.ts` proxies them to `127.0.0.1:8000`.
- **`@/*` alias = `frontend/src/*`** — always import components and lib using `@/`.
- **Brand color is `bg-brand` / `text-brand`** (Tailwind custom, `#3b82d4`) — do not hardcode the hex in new components.
- **API types in `frontend/src/lib/api.ts` must mirror `backend/models/schemas.py`** — update both when the schema changes.
- **UI strings are Traditional Chinese (廣東話)** — keep new visible text consistent with existing UI language.
