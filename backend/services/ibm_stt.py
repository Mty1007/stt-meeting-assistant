"""
IBM Watson Speech-to-Text service.
Uses the zh-CN_CantoneseBroadbandModel for Cantonese + English code-switching.
"""
import asyncio
import structlog
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from functools import lru_cache

from config import get_settings
from models.schemas import SpeakerSegment

log = structlog.get_logger()
settings = get_settings()

# IBM Watson STT pricing: $0.01 per minute (as of 2024)
COST_PER_MINUTE_USD = 0.01


@lru_cache(maxsize=1)
def _get_client() -> SpeechToTextV1:
    authenticator = IAMAuthenticator(settings.IBM_STT_API_KEY)
    client = SpeechToTextV1(authenticator=authenticator)
    client.set_service_url(settings.IBM_STT_URL)
    return client


def _transcribe_segment_sync(audio_path: str, start: float, end: float) -> str:
    """Extract a time segment from WAV and send to IBM Watson STT."""
    audio = AudioSegment.from_wav(audio_path)
    segment_ms = audio[int(start * 1000): int(end * 1000)]

    # Export segment to in-memory bytes
    import io
    buffer = io.BytesIO()
    segment_ms.export(buffer, format="wav")
    buffer.seek(0)

    client = _get_client()
    result = client.recognize(
        audio=buffer,
        content_type="audio/wav",
        model="zh-CN_BroadbandModel",
        # Enable smart formatting for numbers, dates, etc.
        smart_formatting=True,
        # Enable word confidence scores
        word_confidence=False,
        # Allow English words in Cantonese audio
        language_customization_id=None,
    ).get_result()

    transcripts = result.get("results", [])
    if not transcripts:
        return ""
    return " ".join(
        r["alternatives"][0]["transcript"]
        for r in transcripts
        if r.get("alternatives")
    ).strip()


async def transcribe_ibm(
    audio_path: str,
    diarization_segments: list[dict],
) -> tuple[list[SpeakerSegment], float]:
    """
    Transcribe each diarization segment with IBM Watson STT.

    Returns:
        (list of SpeakerSegment, estimated_cost_usd)
    """
    loop = asyncio.get_running_loop()
    speaker_segments: list[SpeakerSegment] = []
    total_duration_minutes = 0.0

    for seg in diarization_segments:
        start, end = seg["start"], seg["end"]
        duration = end - start
        total_duration_minutes += duration / 60.0

        # Run blocking IBM SDK call in thread pool
        text = await loop.run_in_executor(
            None, _transcribe_segment_sync, audio_path, start, end
        )

        if text:
            speaker_segments.append(
                SpeakerSegment(
                    speaker=seg["speaker"],
                    start=start,
                    end=end,
                    text=text,
                )
            )

    cost = round(total_duration_minutes * COST_PER_MINUTE_USD, 6)
    log.info("ibm_stt_cost", minutes=total_duration_minutes, cost_usd=cost)
    return speaker_segments, cost
