"""
Audio pre-processing utilities.
Converts any audio format to 16kHz mono WAV, which is required by both
pyannote.audio and IBM Watson STT.
"""
import structlog
from pathlib import Path
from pydub import AudioSegment

log = structlog.get_logger()


def prepare_audio(input_path: str) -> str:
    """
    Convert input audio to 16kHz mono WAV.
    Returns path to the converted file (same dir, .wav extension).
    Skips conversion if the file is already a suitable WAV.
    """
    input_path = Path(input_path)
    output_path = input_path.with_suffix(".prepared.wav")

    if output_path.exists():
        return str(output_path)

    log.info("audio_prepare_start", input=str(input_path))
    audio = AudioSegment.from_file(str(input_path))
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(str(output_path), format="wav")
    log.info(
        "audio_prepare_done",
        output=str(output_path),
        duration_ms=len(audio),
    )
    return str(output_path)
