from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from src.data_loader import (
    load_accounts,
    load_tickets
)
from src.utils.sanitizer import safe_log_warning


def parse_iso_datetime(dt_str: Any) -> Optional[datetime]:
    """Defensively parse ISO datetime string, supporting Z and offset notations."""
    if not dt_str or not isinstance(dt_str, str):
        return None
    try:
        clean = dt_str.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as err:
        safe_log_warning(f"Failed to parse datetime '{dt_str}': {err}")
        return None


def get_dataset_reference_date() -> Optional[datetime]:
    """
    Return the latest ticket timestamp in the dataset.
    This serves as a deterministic anchor for relative time calculations.
    """
    tickets = load_tickets()
    if not tickets:
        return None

    timestamps: List[datetime] = []
    for ticket in tickets:
        dt = parse_iso_datetime(ticket.get("created_at"))
        if dt:
            timestamps.append(dt)

    return max(timestamps) if timestamps else None


def get_account_by_id(account_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve an account dictionary by account_id."""
    if not account_id:
        return None

    accounts = load_accounts()
    target_id = str(account_id).strip()

    for account in accounts:
        if account.get("account_id") == target_id:
            return account

    return None


def get_account_tickets(account_id: str) -> List[Dict[str, Any]]:
    """Retrieve all tickets belonging to an account, sorted newest first."""
    if not account_id:
        return []

    tickets = load_tickets()
    account_tickets = [
        t for t in tickets
        if t.get("account_id") == account_id
    ]

    # Sort newest first defensively
    def _sort_key(t):
        dt = parse_iso_datetime(t.get("created_at"))
        return dt.timestamp() if dt else 0.0

    account_tickets.sort(key=_sort_key, reverse=True)
    return account_tickets


def get_last_90_days_tickets(account_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve tickets created within the last 90 days relative to
    the dataset reference date for deterministic analysis.
    """
    tickets = load_tickets()
    reference_date = get_dataset_reference_date()

    if reference_date is None:
        return get_account_tickets(account_id)

    cutoff_date = reference_date - timedelta(days=90)
    filtered_tickets = []

    for ticket in tickets:
        if ticket.get("account_id") != account_id:
            continue

        created_at = parse_iso_datetime(ticket.get("created_at"))
        if created_at and created_at >= cutoff_date:
            filtered_tickets.append(ticket)

    # Sort newest first
    def _sort_key(t):
        dt = parse_iso_datetime(t.get("created_at"))
        return dt.timestamp() if dt else 0.0

    filtered_tickets.sort(key=_sort_key, reverse=True)
    return filtered_tickets