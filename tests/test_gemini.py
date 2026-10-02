import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from google import genai
from src.config import GEMINI_MODEL

# Load variables from .env
load_dotenv()


api_key = os.getenv(
    "GEMINI_API_KEY"
)


print(
    "GEMINI_API_KEY:",
    "SET" if api_key else "NOT SET"
)


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set"
    )


client = genai.Client(
    api_key=api_key
)


response = (
    client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            "Reply with exactly: "
            "Gemini API is working"
        )
    )
)


print(response.text)