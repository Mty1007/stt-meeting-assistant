import structlog
from fastapi import APIRouter, HTTPException

from models.schemas import SummarizeRequest, MeetingMinutes
from services.watsonx import generate_meeting_minutes

log = structlog.get_logger()
router = APIRouter()


@router.post("/summarize", response_model=MeetingMinutes)
async def summarize(req: SummarizeRequest):
    """
    Generate structured meeting minutes from a transcript.
    Language options: cantonese | mandarin | english
    """
    if not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    log.info("summarize_start", job_id=req.job_id, language=req.language)
    minutes = await generate_meeting_minutes(req.transcript, req.language)
    log.info("summarize_done", job_id=req.job_id, language=req.language)
    return minutes
