from typing import List
from src.triage.schemas import TicketTriageResult
from src.utils.sanitizer import safe_log_info, safe_log_warning


def apply_priority_sanity_check(
    result: TicketTriageResult,
    subject: str,
    body: str,
    retrieval_results: List = None
) -> TicketTriageResult:
    """
    Apply conservative, deterministic priority and classification guardrails.

    Rules enforced:
    1. Critical P1 Protection: Outages, widespread business stoppage, security breaches,
       or data loss CANNOT be downgraded below P1.
    2. Feature Request Ceiling: Feature requests, especially those with workarounds,
       cannot be P1 or P2 (capped at P3 or P4).
    3. How-to / Query Ceiling: General questions and how-to requests cannot be P1 or P2 (capped at P4).
    4. Ambiguity & Incomplete Tickets: Extremely brief or vague tickets must set
       needs_clarification=True, confidence='Low', and flag for human review.
    5. False Urgency Guardrail: Urgency buzzwords without technical outage signals do not inflate priority.
    6. Low-Confidence Review: Low confidence or conflicting classifications flag for human review.
    """
    ticket_text = f"{subject} {body}".lower().strip()
    audit_trail: List[str] = []

    # ----------------------------------------------------
    # 1. Critical P1 Outage & Security Signals
    # ----------------------------------------------------
    p1_critical_signals = [
        "production outage",
        "service is down",
        "service is completely down",
        "platform unavailable",
        "completely unavailable",
        "all users",
        "entire platform down",
        "production workflows have stopped",
        "workflows have stopped",
        "data loss",
        "security breach",
        "active exploit",
        "ransomware",
        "unauthorized access to database"
    ]

    has_p1_critical_signal = any(signal in ticket_text for signal in p1_critical_signals)

    if has_p1_critical_signal:
        if result.priority != "P1":
            audit_trail.append(f"Guardrail: Enforced P1 (critical outage signal detected, was {result.priority}).")
            result.priority = "P1"
        else:
            audit_trail.append("Guardrail: Validated P1 critical incident classification.")

        # Outages are Incidents
        if result.issue_category not in ["Incident", "Bug"]:
            result.issue_category = "Incident"

        # Outage with sufficient details does not block on clarification
        if "all users" in ticket_text or "production workflows" in ticket_text:
            result.needs_clarification = False
            result.clarifying_questions = []

        # P1 critical issues should have high visibility
        if result.confidence == "Low":
            result.confidence = "Medium"
            result.confidence_score = max(result.confidence_score, 0.70)

    # ----------------------------------------------------
    # 2. Vague & Incomplete Ticket Detection
    # ----------------------------------------------------
    vague_phrases = [
        "not working",
        "broken",
        "it is broken",
        "please fix",
        "help me",
        "error occurred",
        "something went wrong"
    ]

    is_very_short = len(ticket_text) < 45
    has_only_vague = any(ticket_text.startswith(vp) or ticket_text == vp for vp in vague_phrases)

    if (is_very_short or has_only_vague) and not has_p1_critical_signal:
        result.needs_clarification = True
        result.confidence = "Low"
        result.confidence_score = min(result.confidence_score, 0.35)
        result.flagged_for_human_review = True

        if not result.clarifying_questions:
            result.clarifying_questions = [
                "Could you specify which product or module you are experiencing issues with?",
                "What exact error message or unexpected behavior are you seeing?",
                "What steps can we take to reproduce this issue?"
            ]

        # Vague tickets cannot be P1 or P2
        if result.priority in ["P1", "P2"]:
            audit_trail.append(f"Guardrail: Capped vague ticket from {result.priority} to P3.")
            result.priority = "P3"

        audit_trail.append("Guardrail: Flagged incomplete ticket for clarification and human review.")

    # ----------------------------------------------------
    # 3. Feature Request with Workaround Guardrail
    # ----------------------------------------------------
    workaround_signals = [
        "workaround",
        "manual",
        "one-by-one",
        "manually",
        "work-around"
    ]
    has_workaround = any(sig in ticket_text for sig in workaround_signals)

    if result.issue_category == "Feature Request" or "request: bulk" in ticket_text or "feature request" in ticket_text:
        if result.priority in ["P1", "P2"]:
            audit_trail.append(f"Guardrail: Downgraded Feature Request from {result.priority} to P3.")
            result.priority = "P3"

        if has_workaround and result.priority not in ["P3", "P4"]:
            result.priority = "P3"

    # ----------------------------------------------------
    # 4. How-to / Informational Question Guardrail
    # ----------------------------------------------------
    how_to_signals = [
        "how do i",
        "how can i",
        "where can i configure",
        "where do i find",
        "documentation on how",
        "inquiry regarding"
    ]
    is_how_to = any(sig in ticket_text for sig in how_to_signals)

    if (result.issue_category == "How-to" or is_how_to) and not has_p1_critical_signal:
        if result.priority in ["P1", "P2", "P3"]:
            audit_trail.append(f"Guardrail: Capped How-to inquiry from {result.priority} to P4.")
            result.priority = "P4"
            if result.issue_category != "How-to":
                result.issue_category = "How-to"

    # ----------------------------------------------------
    # 5. Low-Confidence and Human Review Flagging
    # ----------------------------------------------------
    if result.confidence == "Low" or result.confidence_score < 0.60 or result.needs_clarification:
        result.flagged_for_human_review = True
        audit_trail.append("Flagged for human review: Low confidence prediction or clarification required.")

    # Append to existing audit notes
    if audit_trail:
        existing_notes = result.audit_notes.strip()
        joined_notes = " | ".join(audit_trail)
        result.audit_notes = f"{existing_notes} [{joined_notes}]" if existing_notes else joined_notes

    return result