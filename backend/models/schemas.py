from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class STTEngine(str, Enum):
    IBM = "ibm"
    ELEVENLABS = "elevenlabs"


class SummaryLanguage(str, Enum):
    CANTONESE = "cantonese"
    MANDARIN = "mandarin"
    ENGLISH = "english"


class SpeakerSegment(BaseModel):
    speaker: str
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    job_id: str
    engine: STTEngine
    segments: list[SpeakerSegment]
    full_transcript: str
    duration_seconds: float
    processing_time_seconds: float
    estimated_cost_usd: float


class SummarizeRequest(BaseModel):
    job_id: str
    transcript: str
    language: SummaryLanguage = SummaryLanguage.CANTONESE


class MeetingMinutes(BaseModel):
    language: SummaryLanguage
    summary: str
    key_points: list[str]
    decisions: list[str]
    action_items: list[dict]
    raw_output: str


class TranscribeRequest(BaseModel):
    job_id: str
    engine: STTEngine = STTEngine.IBM


# NOTE: JobStatus is defined here for future async job-queue support
# but is not yet used by any router.
class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending" | "processing" | "done" | "error"
    message: Optional[str] = None
    result: Optional[TranscriptionResult] = None
