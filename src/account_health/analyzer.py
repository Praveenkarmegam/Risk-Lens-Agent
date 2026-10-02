from collections import Counter
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from src.utils.sanitizer import safe_log_warning


def calculate_seat_utilization(account: Dict[str, Any]) -> float:
    """Calculate percentage of licensed seats currently active."""
    licensed = float(account.get("seats_licensed") or 0)
    active = float(account.get("seats_active") or 0)

    if licensed <= 0:
        return 0.0

    return round(min(100.0, max(0.0, (active / licensed) * 100)), 2)


def calculate_days_until_renewal(
    account: Dict[str, Any],
    reference_date: Optional[datetime]
) -> int:
    """Calculate days until contract renewal relative to dataset reference date."""
    renewal_raw = account.get("renewal_date")
    if not renewal_raw:
        return 0

    try:
        # Strip timestamp portion if present
        clean_date_str = str(renewal_raw).split("T")[0].strip()
        renewal_d = date.fromisoformat(clean_date_str)
    except Exception as err:
        safe_log_warning(f"Error parsing renewal_date '{renewal_raw}': {err}")
        return 0

    if reference_date is None:
        ref_d = date.today()
    else:
        ref_d = reference_date.date()

    return (renewal_d - ref_d).days


def analyze_ticket_distribution(tickets: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """Count tickets by category, priority, and status."""
    categories: Counter = Counter()
    priorities: Counter = Counter()
    statuses: Counter = Counter()

    for ticket in tickets:
        cat = ticket.get("category") or "Unknown"
        categories[cat] += 1

        urgency = ticket.get("urgency") or ticket.get("priority") or "Unknown"
        priorities[urgency] += 1

        status = ticket.get("status") or "Unknown"
        statuses[status] += 1

    return {
        "category_distribution": dict(categories),
        "priority_distribution": dict(priorities),
        "status_distribution": dict(statuses)
    }


def build_account_metrics(
    account: Dict[str, Any],
    recent_tickets: List[Dict[str, Any]],
    reference_date: Optional[datetime]
) -> Dict[str, Any]:
    """Build deterministic account metrics payload."""
    seat_utilization = calculate_seat_utilization(account)
    days_until_renewal = calculate_days_until_renewal(account, reference_date)
    ticket_distribution = analyze_ticket_distribution(recent_tickets)

    return {
        "account_id": account.get("account_id", "UNKNOWN"),
        "company": account.get("company", "Unknown"),
        "plan_tier": account.get("plan_tier", "Standard"),
        "arr_usd": account.get("arr_usd", 0),
        "health_status": account.get("health_status", "Healthy"),
        "usage_trend": account.get("usage_trend", "Active"),
        "open_tickets": account.get("open_tickets", 0),
        "p1_tickets_last_30d": account.get("p1_tickets_last_30d", 0),
        "seat_utilization_percent": seat_utilization,
        "days_until_renewal": days_until_renewal,
        "ticket_metrics": ticket_distribution,
        "recent_ticket_count": len(recent_tickets)
    }