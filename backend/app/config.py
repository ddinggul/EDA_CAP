# backend/app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Naver CLOVA Speech Recognition - 단문 인식 (Short Sentence)
    # API 문서: https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-shortsentence
    NAVER_CLOVA_SECRET_KEY: str = os.getenv("NAVER_CLOVA_SECRET_KEY", "")

    # 단문 인식 API endpoint
    # Beta: https://beta-clovaspeech-gw.ncloud.com/recog/v1/stt
    # Production: https://clovaspeech-gw.ncloud.com/recog/v1/stt
    NAVER_CLOVA_STT_ENDPOINT: str = os.getenv(
        "NAVER_CLOVA_STT_ENDPOINT",
        "https://clovaspeech-gw.ncloud.com/recog/v1/stt"
    )

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

    # Application settings
    TEMP_DIR: Path = Path(__file__).parent.parent / "tmp"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".mp3", ".wav", ".m4a", ".ogg", ".webm"}

    def __init__(self):
        # Create temp directory if it doesn't exist
        self.TEMP_DIR.mkdir(exist_ok=True)

settings = Settings()
