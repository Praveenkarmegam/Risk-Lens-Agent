import logging
import re
from typing import Any

# Configure standard logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("RiskLens")

# Patterns for sensitive data sanitization
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
API_KEY_PATTERN = re.compile(r"(?:api[_-]?key|token|bearer|secret)[\s:=]+['\"]?([a-zA-Z0-9_\-\.]{16,})['\"]?", re.IGNORECASE)
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def sanitize_text(text: str) -> str:
    """
    Mask sensitive personally identifiable information (PII)
    and credentials from strings before logging or external API transmission.
    """
    if not isinstance(text, str):
        return text

    sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    sanitized = CREDIT_CARD_PATTERN.sub("[REDACTED_CARD]", sanitized)
    sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    
    # Mask API keys and secrets
    def _mask_secret(match):
        full_match = match.group(0)
        secret = match.group(1)
        return full_match.replace(secret, "[REDACTED_SECRET]")

    sanitized = API_KEY_PATTERN.sub(_mask_secret, sanitized)
    return sanitized


def safe_log_info(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log an info message with PII sanitization."""
    logger.info(sanitize_text(msg), *args, **kwargs)


def safe_log_warning(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log a warning message with PII sanitization."""
    logger.warning(sanitize_text(msg), *args, **kwargs)


def safe_log_error(msg: str, *args: Any, **kwargs: Any) -> None:
    """Log an error message with PII sanitization."""
    logger.error(sanitize_text(msg), *args, **kwargs)
