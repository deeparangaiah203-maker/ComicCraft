from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.templates_dir = self.base_dir / "templates"
        self.static_dir = self.base_dir / "static"
        self.exports_dir = self.base_dir / "exports"
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.hf_api_key = os.getenv("HF_API_KEY", "")
        self.app_host = os.getenv("APP_HOST", "127.0.0.1")
        self.app_port = int(os.getenv("APP_PORT", "8000"))

    def ensure_directories(self):
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
