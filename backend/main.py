import os
import uuid
import logging
import structlog
from pathlib import Path

try:
    import instana  # optional — only active when INSTANA_AGENT_KEY is set
except ImportError:
    pass
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from routers import upload, transcribe, summarize

# ── Structured logging ────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

# ── App ───────────────────────────────────────────────────────────────────────
settings = get_settings()
app = FastAPI(
    title="STT Meeting Assistant",
    version="1.0.0",
    description="Cantonese-English mixed speech transcription & meeting minutes",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Ensure upload dir ─────────────────────────────────────────────────────────
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# ── Request ID middleware ─────────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(transcribe.router, prefix="/api", tags=["transcribe"])
app.include_router(summarize.router, prefix="/api", tags=["summarize"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
