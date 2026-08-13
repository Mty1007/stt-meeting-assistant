"""
watsonx.ai meeting minutes generation.
Uses IBM Granite model to produce structured meeting summaries in
Cantonese (Traditional Chinese), Mandarin (Simplified Chinese), or English.
"""
import re
import json
import asyncio
import structlog
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from functools import lru_cache

from config import get_settings
from models.schemas import MeetingMinutes, SummaryLanguage

log = structlog.get_logger()
settings = get_settings()

# Language instruction map
_LANG_INSTRUCTION: dict[SummaryLanguage, str] = {
    SummaryLanguage.CANTONESE: "繁體中文（粵語書面語，例如使用「係」「唔係」「點解」「咁」等粵語詞彙）",
    SummaryLanguage.MANDARIN:  "简体中文（普通话）",
    SummaryLanguage.ENGLISH:   "English",
}


@lru_cache(maxsize=1)
def _get_model() -> ModelInference:
    credentials = Credentials(
        url=settings.WATSONX_URL,
        api_key=settings.WATSONX_API_KEY,
    )
    client = APIClient(credentials=credentials, project_id=settings.WATSONX_PROJECT_ID)
    model = ModelInference(
        model_id="ibm/granite-13b-chat-v2",
        api_client=client,
        params={
            GenParams.MAX_NEW_TOKENS: 1500,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_P: 0.9,
        },
    )
    return model


def _build_prompt(transcript: str, language: SummaryLanguage) -> str:
    lang_instruction = _LANG_INSTRUCTION[language]
    return f"""You are a professional meeting secretary specializing in Hong Kong business meetings.
The following transcript contains Cantonese and English mixed speech (code-switching).

TRANSCRIPT:
{transcript}

Please produce meeting minutes in {lang_instruction}.
Output ONLY valid JSON matching this exact structure (no extra text):
{{
  "summary": "2-4 sentence overview of the meeting",
  "key_points": ["point 1", "point 2", "point 3"],
  "decisions": ["decision 1", "decision 2"],
  "action_items": [
    {{"owner": "name or speaker label", "task": "description", "due_date": "if mentioned, else null"}}
  ]
}}
"""


def _parse_response(raw: str, language: SummaryLanguage) -> MeetingMinutes:
    """Extract JSON from model output and map to MeetingMinutes."""
    # Try to find a JSON block in the response
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return MeetingMinutes(
                language=language,
                summary=data.get("summary", ""),
                key_points=data.get("key_points", []),
                decisions=data.get("decisions", []),
                action_items=data.get("action_items", []),
                raw_output=raw,
            )
        except json.JSONDecodeError:
            pass

    # Fallback: return raw output as summary
    log.warning("watsonx_json_parse_failed", raw_preview=raw[:200])
    return MeetingMinutes(
        language=language,
        summary=raw.strip(),
        key_points=[],
        decisions=[],
        action_items=[],
        raw_output=raw,
    )


async def generate_meeting_minutes(
    transcript: str,
    language: SummaryLanguage,
) -> MeetingMinutes:
    """
    Call watsonx.ai to generate structured meeting minutes.
    Runs the blocking SDK call in a thread pool to stay async-safe.
    """
    prompt = _build_prompt(transcript, language)
    model = _get_model()

    loop = asyncio.get_running_loop()
    raw = await loop.run_in_executor(
        None,
        lambda: model.generate_text(prompt=prompt),
    )

    log.info("watsonx_response_received", length=len(raw), language=language)
    return _parse_response(raw, language)
