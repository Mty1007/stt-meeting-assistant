"""
ElevenLabs Scribe v1 STT service.
Scribe natively handles multilingual (Cantonese + English) code-switching.
"""
import io
import asyncio
import structlog
import httpx
from pydub import AudioSegment

from config import get_settings
from models.schemas import SpeakerSegment

log = structlog.get_logger()
settings = get_settings()

ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"

# ElevenLabs Scribe pricing: $0.40 per hour = $0.00667 per minute
COST_PER_MINUTE_USD = 0.40 / 60


async def _transcribe_segment(
    client: httpx.AsyncClient,
    audio_path: str,
    start: float,
    end: float,
) -> str:
    """Extract a segment and transcribe via ElevenLabs Scribe."""
    audio = AudioSegment.from_wav(audio_path)
    segment_ms = audio[int(start * 1000): int(end * 1000)]

    buffer = io.BytesIO()
    segment_ms.export(buffer, format="wav")
    buffer.seek(0)

    response = await client.post(
        ELEVENLABS_STT_URL,
        headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
        files={"file": ("segment.wav", buffer, "audio/wav")},
        data={
            "model_id": "scribe_v1",
            # Hint: Cantonese + English — let Scribe auto-detect
            "language_code": "yue",  # ISO 639-3 for Cantonese
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json().get("text", "").strip()


async def transcribe_elevenlabs(
    audio_path: str,
    diarization_segments: list[dict],
) -> tuple[list[SpeakerSegment], float]:
    """
    Transcribe each diarization segment with ElevenLabs Scribe v1.

    Returns:
        (list of SpeakerSegment, estimated_cost_usd)
    """
    speaker_segments: list[SpeakerSegment] = []
    total_duration_minutes = 0.0

    async with httpx.AsyncClient() as client:
        tasks = [
            _transcribe_segment(client, audio_path, seg["start"], seg["end"])
            for seg in diarization_segments
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for seg, text_or_err in zip(diarization_segments, results):
        duration = seg["end"] - seg["start"]
        total_duration_minutes += duration / 60.0

        if isinstance(text_or_err, Exception):
            log.error(
                "elevenlabs_segment_error",
                speaker=seg["speaker"],
                start=seg["start"],
                error=str(text_or_err),
            )
            continue

        if text_or_err:
            speaker_segments.append(
                SpeakerSegment(
                    speaker=seg["speaker"],
                    start=seg["start"],
                    end=seg["end"],
                    text=text_or_err,
                )
            )

    cost = round(total_duration_minutes * COST_PER_MINUTE_USD, 6)
    log.info("elevenlabs_stt_cost", minutes=total_duration_minutes, cost_usd=cost)
    return speaker_segments, cost
