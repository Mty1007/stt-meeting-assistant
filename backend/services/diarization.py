"""
Speaker diarization using pyannote.audio 3.x.
Splits audio into segments labelled by speaker identity.
"""
import structlog
from functools import lru_cache
from pyannote.audio import Pipeline
import torch

from config import get_settings

log = structlog.get_logger()
settings = get_settings()


@lru_cache(maxsize=1)
def _get_pipeline() -> Pipeline:
    """Load pipeline once and cache it (heavy model ~1 GB)."""
    log.info("diarization_model_loading")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=settings.HUGGINGFACE_TOKEN,
    )
    # Use GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)
    log.info("diarization_model_ready", device=str(device))
    return pipeline


def diarize_audio(audio_path: str) -> list[dict]:
    """
    Run speaker diarization on a 16kHz mono WAV file.

    Returns a list of segments:
        [{"speaker": "SPEAKER_00", "start": 0.0, "end": 15.3}, ...]
    """
    pipeline = _get_pipeline()
    diarization = pipeline(audio_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        # Skip very short segments (< 0.5s) — usually noise
        if turn.end - turn.start < 0.5:
            continue
        segments.append({
            "speaker": speaker,
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
        })

    log.info("diarization_segments", count=len(segments))
    return segments
