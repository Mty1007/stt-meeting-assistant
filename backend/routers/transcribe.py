import time
import structlog
from pathlib import Path
from fastapi import APIRouter, HTTPException

from config import get_settings
from models.schemas import TranscribeRequest, TranscriptionResult, STTEngine
from services.audio_processor import prepare_audio
from services.diarization import diarize_audio
from services.ibm_stt import transcribe_ibm
from services.elevenlabs_stt import transcribe_elevenlabs

log = structlog.get_logger()
router = APIRouter()
settings = get_settings()


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe(req: TranscribeRequest):
    """
    Run speaker diarization + STT on a previously uploaded audio file.
    """
    # ── 1. Locate the uploaded file ───────────────────────────────────────────
    upload_dir = Path(settings.UPLOAD_DIR)
    matches = list(upload_dir.glob(f"{req.job_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail=f"No file found for job_id={req.job_id}")
    raw_audio_path = str(matches[0])

    start_time = time.monotonic()

    # ── 2. Convert to 16kHz mono WAV (required by pyannote + Watson) ──────────
    prepared_path = prepare_audio(raw_audio_path)

    # ── 3. Speaker diarization ────────────────────────────────────────────────
    log.info("diarization_start", job_id=req.job_id)
    diarization_segments = diarize_audio(prepared_path)
    log.info("diarization_done", job_id=req.job_id, num_segments=len(diarization_segments))

    if not diarization_segments:
        raise HTTPException(status_code=422, detail="No speech detected in the audio file.")

    # ── 4. STT per segment ────────────────────────────────────────────────────
    log.info("stt_start", job_id=req.job_id, engine=req.engine)
    if req.engine == STTEngine.IBM:
        segments, cost = await transcribe_ibm(prepared_path, diarization_segments)
    else:
        segments, cost = await transcribe_elevenlabs(prepared_path, diarization_segments)

    # ── 5. Build full transcript text ─────────────────────────────────────────
    full_transcript = "\n".join(
        f"[{s.speaker}] ({s.start:.1f}s - {s.end:.1f}s): {s.text}"
        for s in segments
    )

    processing_time = round(time.monotonic() - start_time, 2)
    log.info(
        "transcription_complete",
        job_id=req.job_id,
        engine=req.engine,
        processing_time=processing_time,
        cost_usd=cost,
    )

    return TranscriptionResult(
        job_id=req.job_id,
        engine=req.engine,
        segments=segments,
        full_transcript=full_transcript,
        duration_seconds=segments[-1].end if segments else 0,
        processing_time_seconds=processing_time,
        estimated_cost_usd=cost,
    )
