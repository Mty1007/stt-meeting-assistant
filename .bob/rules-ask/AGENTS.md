# Documentation Context (Non-Obvious)

- **README is in Traditional Chinese** — the only English docs are inline code comments and this file.
- **No test suite** — there are no unit/integration tests anywhere in the repo; do not reference test files when answering.
- **`JobStatus` schema exists but is unused** — `backend/models/schemas.py` defines `JobStatus` with a comment "not yet used by any router"; it is forward-looking scaffolding for async job queues.
- **Two separate type systems** — `STTEngine`, `SpeakerSegment`, `TranscriptionResult`, `MeetingMinutes` are defined in both `backend/models/schemas.py` (Pydantic) and `frontend/src/lib/api.ts` (TypeScript). They must be kept in sync manually.
- **Instana is optional** — `main.py` imports it inside a `try/except`; it only activates when `INSTANA_AGENT_KEY` is set.
- **pyannote requires gated model access** — `HUGGINGFACE_TOKEN` is not enough alone; the user must accept license terms for both `pyannote/speaker-diarization-3.1` AND `pyannote/segmentation-3.0` on huggingface.co.
- **ElevenLabs language code** — the service sends `language_code: "yue"` (ISO 639-3 for Cantonese), not the more common `"zh"`.
