from src.account_health.schemas import FlaggedIssue
import re


def detect_account_risks(account, tickets):
    """
    Detect account-level and ticket-level risks
    using deterministic rules.

    Ticket evidence is extracted directly from
    the original ticket text.

    This function intentionally avoids LLM-based
    risk detection so results remain deterministic.
    """

    if account is None:
        raise ValueError(
            "Cannot detect account risks: "
            "account data is missing."
        )

    risks = []

    # ==================================
    # ACCOUNT-LEVEL RISKS
    # ==================================

    # Account explicitly marked as At Risk
    if account.get("health_status") == "At Risk":
        risks.append(
            FlaggedIssue(
                risk_type="Account Health",
                severity="High",
                source="account",
                reason=(
                    "Account is explicitly "
                    "marked as At Risk."
                )
            )
        )

    # Inactive / declining usage
    if account.get("usage_trend") == "Inactive":
        risks.append(
            FlaggedIssue(
                risk_type="Usage Decline",
                severity="High",
                source="account",
                reason=(
                    "Account usage trend "
                    "is 'Inactive'."
                )
            )
        )

    elif account.get("usage_trend") == "Declining":
        risks.append(
            FlaggedIssue(
                risk_type="Usage Decline",
                severity="Medium",
                source="account",
                reason=(
                    "Account usage trend "
                    "is 'Declining'."
                )
            )
        )

    # High open ticket volume
    #
    # Dataset analysis showed that 11 is the maximum
    # open ticket count. Accounts with 10+ open tickets
    # are therefore treated as elevated support risk.
    open_tickets = account.get("open_tickets", 0)

    if open_tickets >= 10:
        risks.append(
            FlaggedIssue(
                risk_type="High Support Load",
                severity="Medium",
                source="account",
                reason=(
                    f"Account currently has "
                    f"{open_tickets} open tickets, "
                    f"indicating elevated unresolved "
                    f"support volume."
                )
            )
        )

    # P1 incidents in the last 30 days
    p1_tickets = account.get(
        "p1_tickets_last_30d",
        0
    )

    if p1_tickets >= 3:
        risks.append(
            FlaggedIssue(
                risk_type="Recent Critical Incidents",
                severity="High",
                source="account",
                reason=(
                    f"Account has experienced "
                    f"{p1_tickets} P1 tickets "
                    f"in the last 30 days."
                )
            )
        )

    elif p1_tickets > 0:
        risks.append(
            FlaggedIssue(
                risk_type="Recent Critical Incidents",
                severity="Medium",
                source="account",
                reason=(
                    f"Account has experienced "
                    f"{p1_tickets} P1 ticket(s) "
                    f"in the last 30 days."
                )
            )
        )

    # Low seat utilization
    seats_licensed = account.get(
        "seats_licensed",
        0
    )

    seats_active = account.get(
        "seats_active",
        0
    )

    if seats_licensed > 0:
        seat_utilization = (
            seats_active / seats_licensed
        ) * 100

        if seat_utilization < 40:
            risks.append(
                FlaggedIssue(
                    risk_type="Low Product Adoption",
                    severity="Medium",
                    source="account",
                    reason=(
                        f"Only {seat_utilization:.2f}% "
                        f"of licensed seats are active."
                    )
                )
            )

    # Escalation notes
    escalation_notes = (
        account.get("escalation_notes")
        or []
    )

    for note in escalation_notes:
        risks.append(
            FlaggedIssue(
                risk_type="Escalation Signal",
                severity="High",
                source="account",
                reason=note
            )
        )

    # ==================================
    # TICKET-LEVEL RISKS
    # ==================================

    for ticket in tickets:
        ticket_id = ticket.get("ticket_id")

        subject = ticket.get(
            "subject",
            ""
        )

        body = ticket.get(
            "body",
            ""
        )

        full_text = f"{subject}\n{body}"
        lower_text = full_text.lower()

        # ------------------------------
        # Direct churn signals
        # ------------------------------

        churn_phrases = [
            "switching vendors",
            "switch vendor",
            "competing vendor",
            "competitor",
            "not renew",
            "won't renew",
            "will not renew",
            "cancel our contract",
            "terminate our contract",
            "cancellation",
        ]

        for phrase in churn_phrases:
            if phrase in lower_text:
                quote = extract_evidence_quote(
                    subject,
                    body,
                    phrase
                )

                risks.append(
                    FlaggedIssue(
                        risk_type="Churn Risk",
                        severity="High",
                        source="ticket",
                        reason=(
                            "Ticket contains direct "
                            "churn or vendor-switching "
                            "language."
                        ),
                        ticket_id=ticket_id,
                        evidence_quote=quote
                    )
                )

                break

        # ------------------------------
        # Strong escalation signals
        # ------------------------------

        escalation_phrases = [
            "please escalate immediately",
            "business continuity at risk",
            "executive escalation",
            "this is a p1 for us",
            "escalate this",
        ]

        for phrase in escalation_phrases:
            if phrase in lower_text:
                quote = extract_evidence_quote(
                    subject,
                    body,
                    phrase
                )

                risks.append(
                    FlaggedIssue(
                        risk_type="Escalation Signal",
                        severity="High",
                        source="ticket",
                        reason=(
                            "Ticket contains an "
                            "explicit escalation "
                            "signal."
                        ),
                        ticket_id=ticket_id,
                        evidence_quote=quote
                    )
                )

                break

        # ------------------------------
        # Customer dissatisfaction
        # ------------------------------

        dissatisfaction_phrases = [
            "unacceptable",
            "extremely disappointed",
            "frustrated",
            "losing confidence",
        ]

        for phrase in dissatisfaction_phrases:
            if phrase in lower_text:
                quote = extract_evidence_quote(
                    subject,
                    body,
                    phrase
                )

                risks.append(
                    FlaggedIssue(
                        risk_type="Customer Dissatisfaction",
                        severity="Medium",
                        source="ticket",
                        reason=(
                            "Ticket contains strong "
                            "customer dissatisfaction "
                            "language."
                        ),
                        ticket_id=ticket_id,
                        evidence_quote=quote
                    )
                )

                break

    return risks


def extract_evidence_quote(
    subject,
    body,
    phrase
):
    """
    Return an exact quote from the original
    subject or body containing the phrase.

    No LLM rewriting is used.
    """

    phrase_lower = phrase.lower()

    # Check subject first
    if phrase_lower in subject.lower():
        return subject.strip()

    # Split body into sentence-like units
    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        body
    )

    for sentence in sentences:
        if phrase_lower in sentence.lower():
            return sentence.strip()

    # Fallback to exact phrase
    return phrase
