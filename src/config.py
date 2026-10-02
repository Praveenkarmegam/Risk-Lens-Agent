import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Gemini API Key (do not crash on import if missing, validate when initializing client)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini Model
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
)

# Request timeout in seconds
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

# Max retry attempts for API calls
GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "4"))

# Data directory resolution (support data_risklens with data fallback)
if (BASE_DIR / "data_risklens").exists():
    DATA_DIR = BASE_DIR / "data_risklens"
elif (BASE_DIR / "data").exists():
    DATA_DIR = BASE_DIR / "data"
else:
    DATA_DIR = BASE_DIR / "data_risklens"

TICKETS_PATH = DATA_DIR / "tickets.json"
ACCOUNTS_PATH = DATA_DIR / "accounts.json"

# Knowledge base path resolution (support knowledge-base-risklens with knowledge-base fallback)
if (BASE_DIR / "knowledge-base-risklens").exists():
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base-risklens"
elif (BASE_DIR / "knowledge-base").exists():
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base"
else:
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge-base-risklens"


def is_gemini_configured() -> bool:
    """Check if a Gemini API key is available in the environment."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())