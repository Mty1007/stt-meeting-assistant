from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # IBM Watson STT
    IBM_STT_API_KEY: str = ""
    IBM_STT_URL: str = ""

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""

    # watsonx.ai
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"

    # pyannote (Hugging Face token to download model)
    HUGGINGFACE_TOKEN: str = ""

    # Instana
    INSTANA_AGENT_KEY: str = ""
    INSTANA_ENDPOINT_URL: str = ""

    # App
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 500

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
