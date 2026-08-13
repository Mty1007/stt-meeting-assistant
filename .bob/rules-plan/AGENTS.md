# Architecture Rules (Non-Obvious)

- **Strictly 3-step, 3-endpoint flow** — upload → transcribe → summarize. Each step requires the `job_id` from the previous step. There is no single combined endpoint.
- **Uploaded files are persisted on disk, not in memory** — `backend/uploads/` stores `<job_id>.<ext>` and `<job_id>.prepared.wav`. These are never cleaned up automatically; plan for disk management if deploying.
- **Transcription is synchronous and can take minutes** — the `/api/transcribe` endpoint blocks until diarization + all STT calls finish. ElevenLabs segments run concurrently; IBM segments run serially in a thread pool. Long recordings will time out nginx/proxies with default settings.
- **Models are process-global singletons** — pyannote pipeline, IBM Watson client, and watsonx.ai `ModelInference` are each cached via `@lru_cache(maxsize=1)`. Restarting the process clears them; multi-worker deployments (`uvicorn --workers N`) will load N copies.
- **watsonx.ai uses Granite-13b-chat-v2** — model ID is hard-coded in `watsonx.py`. The prompt instructs JSON-only output; a regex fallback handles malformed responses by returning the raw text as the summary.
- **CORS is hard-coded to `http://localhost:3000`** — production deployment requires updating `allow_origins` in `main.py`.
- **Audio must be 16 kHz mono WAV before reaching pyannote or Watson** — `audio_processor.py` handles this conversion; the prepared file is cached (`output.exists()` check). Any new STT engine must accept this format or add its own preparation step.
- **No database, no auth, no job queue** — state lives entirely in uploaded files on disk and in-memory caches. `JobStatus` is scaffolded but not wired.
