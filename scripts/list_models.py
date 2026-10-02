import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from google import genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is not set.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("Available Gemini Models:")
print("-" * 40)
for model in client.models.list():
    print(f"- {model.name}")
