import os
import time
import random
from typing import Any, Optional
from google import genai
from google.genai.errors import ClientError, APIError
from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MAX_RETRIES,
    GEMINI_TIMEOUT_SECONDS,
    is_gemini_configured,
)
from src.utils.sanitizer import safe_log_warning, safe_log_error, safe_log_info


def get_gemini_client() -> genai.Client:
    """
    Create and return an authenticated Gemini API client.
    Raises ValueError with actionable instructions if GEMINI_API_KEY is missing.
    """
    if not is_gemini_configured():
        raise ValueError(
            "GEMINI_API_KEY is not set or empty. "
            "Please configure GEMINI_API_KEY in your .env file or environment variables."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_with_retry(
    client: genai.Client,
    model: str = GEMINI_MODEL,
    contents: Any = "",
    config: Optional[Any] = None,
    max_retries: int = GEMINI_MAX_RETRIES,
    base_delay: float = 3.0
) -> Any:
    """
    Execute Gemini model content generation with exponential backoff and jitter
    for transient errors (429 Rate Limit, 503 Unavailable, 504 Gateway Timeout).
    Separates network/API execution from business logic.
    """
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            return response
        except (ClientError, APIError) as error:
            last_error = error
            error_message = str(error)

            # Check for transient rate limit or availability errors
            is_rate_limit = "429" in error_message or "RESOURCE_EXHAUSTED" in error_message
            is_server_error = "503" in error_message or "504" in error_message or "UNAVAILABLE" in error_message

            if (is_rate_limit or is_server_error) and attempt < max_retries:
                # Exponential backoff with jitter
                sleep_time = min(30.0, base_delay * (2 ** attempt)) + random.uniform(0.2, 1.0)
                safe_log_warning(
                    f"[Gemini API] Transient error (attempt {attempt + 1}/{max_retries}): {error_message}. "
                    f"Retrying in {sleep_time:.2f} seconds..."
                )
                time.sleep(sleep_time)
                continue
            elif is_rate_limit and attempt >= max_retries:
                safe_log_error(f"[Gemini API] Quota exhausted after {max_retries} retries: {error_message}")
                raise RuntimeError(
                    "Gemini API quota is currently exhausted after max retries. "
                    "Please wait for your quota to reset or verify API billing settings."
                ) from error
            else:
                safe_log_error(f"[Gemini API] Non-retryable client error: {error_message}")
                raise
        except Exception as err:
            last_error = err
            safe_log_error(f"[Gemini API] Unexpected error during generate_content: {err}")
            if attempt < max_retries:
                sleep_time = base_delay + random.uniform(0.1, 0.5)
                time.sleep(sleep_time)
                continue
            raise

    if last_error:
        raise last_error