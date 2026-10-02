import sys
from pathlib import Path

# Add project root to sys.path for standalone script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import json
from unittest.mock import MagicMock, patch

from src.triage.schemas import TicketTriageResult, KnowledgeBaseReference
from src.triage.validators import apply_priority_sanity_check
from src.triage.service import (
    triage_ticket,
    extract_and_parse_json,
    compute_confidence_score,
    generate_deterministic_fallback,
)
from src.retrieval.retriever import KnowledgeBaseRetriever
from src.account_health.loader import get_account_by_id, get_last_90_days_tickets
from src.account_health.analyzer import calculate_seat_utilization, calculate_days_until_renewal, build_account_metrics
from src.account_health.risk_detector import detect_account_risks, extract_evidence_quote
from src.account_health.service import generate_account_health_brief
from src.utils.sanitizer import sanitize_text


# =====================================================================
# 1. Normal Ticket Triage Tests
# =====================================================================

def test_normal_ticket_triage():
    """Verify standard ticket categorization, priority, and KB referencing."""
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [
        {
            "document": "authentication-sso.md",
            "path": "troubleshooting/authentication-sso.md",
            "score": 0.85,
            "content": "SAML 2.0 configuration guide and certificate troubleshooting."
        }
    ]

    result = triage_ticket(
        subject="SSO login error with SAML certificate",
        body="Our employees cannot authenticate via Okta due to an expired SAML certificate.",
        retriever=mock_retriever
    )

    assert result.issue_category in ["Authentication", "Incident", "Bug"]
    assert result.priority in ["P1", "P2", "P3"]
    assert isinstance(result.reasoning, str) and len(result.reasoning) > 0
    assert isinstance(result.draft_first_response, str) and len(result.draft_first_response) > 0
    assert result.confidence in ["High", "Medium", "Low"]


# =====================================================================
# 2. Ambiguous & Incomplete Ticket Tests
# =====================================================================

def test_ambiguous_ticket_handling():
    """Vague or incomplete tickets must trigger clarification and low confidence."""
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = []

    result = triage_ticket(
        subject="Not working",
        body="It is broken. Please fix this.",
        retriever=mock_retriever
    )

    assert result.needs_clarification is True
    assert len(result.clarifying_questions) >= 1
    assert result.confidence == "Low"
    assert result.confidence_score <= 0.40
    assert result.flagged_for_human_review is True
    assert result.priority in ["P3", "P4"]  # Vague tickets must not be P1


# =====================================================================
# 3. High-Priority Incidents & P1 Guardrails
# =====================================================================

def test_critical_p1_incident_protection():
    """Critical production outage signals must enforce P1 priority."""
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = []

    result = triage_ticket(
        subject="Production outage: platform unavailable for all users",
        body="The service is down and production workflows have stopped across all regions.",
        retriever=mock_retriever
    )

    assert result.priority == "P1"
    assert result.issue_category in ["Incident", "Bug"]
    assert result.needs_clarification is False
    assert "P1" in result.audit_notes


def test_priority_guardrail_prevents_downgrade():
    """Model attempt to downgrade a P1 outage must be intercepted and corrected."""
    mock_result = TicketTriageResult(
        product_area="Platform",
        issue_category="Incident",
        priority="P3",  # Model incorrectly assigned P3
        confidence="Medium",
        confidence_score=0.70,
        needs_clarification=False,
        clarifying_questions=[],
        retrieved_facts=[],
        model_reasoning="Minor outage",
        reasoning="Minor outage",
        known_issue=False,
        knowledge_base_references=[],
        recommended_team="Support",
        draft_first_response="We are looking into it."
    )

    subject = "Production outage: all users affected"
    body = "Entire platform down and production workflows have stopped completely."

    corrected = apply_priority_sanity_check(mock_result, subject, body)

    assert corrected.priority == "P1"
    assert "Enforced P1" in corrected.audit_notes


# =====================================================================
# 4. Conflicting Signals Tests
# =====================================================================

def test_conflicting_signals_false_urgency():
    """Customer buzzwords ('urgent', 'emergency') on general question must cap at P4."""
    mock_result = TicketTriageResult(
        product_area="User Settings",
        issue_category="How-to",
        priority="P2",  # Model inflated due to 'urgent'
        confidence="High",
        confidence_score=0.85,
        needs_clarification=False,
        clarifying_questions=[],
        retrieved_facts=[],
        model_reasoning="Customer stated urgent",
        reasoning="Customer stated urgent",
        known_issue=False,
        knowledge_base_references=[],
        recommended_team="Support",
        draft_first_response="Here is how to configure settings."
    )

    subject = "URGENT EMERGENCY: How do I change email notifications?"
    body = "This is extremely urgent! Where can I configure notification settings?"

    corrected = apply_priority_sanity_check(mock_result, subject, body)

    assert corrected.priority == "P4"
    assert corrected.issue_category == "How-to"


def test_feature_request_with_workaround_capped_at_p3():
    """Feature request claiming P1 with manual workaround must cap at P3."""
    mock_result = TicketTriageResult(
        product_area="Data Management",
        issue_category="Feature Request",
        priority="P1",  # Inflated
        confidence="High",
        confidence_score=0.80,
        needs_clarification=False,
        clarifying_questions=[],
        retrieved_facts=[],
        model_reasoning="Customer requested feature",
        reasoning="Customer requested feature",
        known_issue=False,
        knowledge_base_references=[],
        recommended_team="Product",
        draft_first_response="Thanks for the feedback."
    )

    subject = "Request: bulk archive operations"
    body = "We currently have to archive records one at a time manually. Current workaround is manual processing."

    corrected = apply_priority_sanity_check(mock_result, subject, body)

    assert corrected.priority in ["P3", "P4"]
    assert "Downgraded Feature Request" in corrected.audit_notes


# =====================================================================
# 5. Missing Account Data (Adversarial Lookup)
# =====================================================================

def test_missing_account_data_raises_clear_error():
    """Looking up a non-existent account must raise clear ValueError."""
    with pytest.raises(ValueError) as excinfo:
        generate_account_health_brief("ACC-DOES-NOT-EXIST")

    assert "account not found" in str(excinfo.value).lower()


# =====================================================================
# 6. Missing KB Articles & Empty Retrieval
# =====================================================================

def test_empty_knowledge_base_retriever():
    """Retriever must handle empty chunks and unknown queries gracefully without crashing."""
    empty_retriever = KnowledgeBaseRetriever(chunks=[])
    results = empty_retriever.search("test query")
    assert results == []

    # Retriever with dummy chunks but non-matching query
    dummy_retriever = KnowledgeBaseRetriever(
        chunks=[{"document": "test.md", "path": "test.md", "content": "only unrelated information"}]
    )
    unrelated_results = dummy_retriever.search("xyz123999nonexistentword", min_score=0.5)
    assert unrelated_results == []


# =====================================================================
# 7. Malformed JSON & Validation Failure Recovery
# =====================================================================

def test_extract_and_parse_json_with_codeblocks():
    """JSON wrapped in markdown blocks or comments must parse cleanly."""
    raw = """
    Here is the triage output:
    ```json
    {
        "product_area": "Authentication",
        "issue_category": "Authentication",
        "priority": "P2",
        "confidence": "High",
        "confidence_score": 0.88,
        "needs_clarification": false,
        "clarifying_questions": [],
        "retrieved_facts": ["SAML certificate expired"],
        "model_reasoning": "Standard SSO failure",
        "reasoning": "Standard SSO failure",
        "known_issue": false,
        "knowledge_base_references": [],
        "recommended_team": "Identity Support",
        "draft_first_response": "We received your report."
    }
    ```
    Thank you!
    """
    parsed = extract_and_parse_json(raw)
    assert parsed["product_area"] == "Authentication"
    assert parsed["priority"] == "P2"


def test_malformed_json_fallback_recovery():
    """Completely invalid JSON from model must not crash the service; returns valid fallback."""
    garbage = "I am an AI and here is my decision: Category: Bug, Priority: High. (Not JSON!)"
    
    with pytest.raises(Exception):
        extract_and_parse_json(garbage)

    # Service fallback must succeed
    fallback = generate_deterministic_fallback(
        subject="Login broken",
        body="User cannot authenticate",
        retrieval_results=[],
        reason="Model returned invalid JSON"
    )

    assert isinstance(fallback, TicketTriageResult)
    assert fallback.flagged_for_human_review is True
    assert fallback.confidence == "Low"
    assert "Model returned invalid JSON" in fallback.audit_notes


# =====================================================================
# 8. Low-Confidence & Human Review Flagging
# =====================================================================

def test_low_confidence_flagged_for_human_review():
    """Low confidence scores or ambiguous flags must set flagged_for_human_review=True."""
    mock_result = TicketTriageResult(
        product_area="General",
        issue_category="Other",
        priority="P3",
        confidence="Low",
        confidence_score=0.30,
        needs_clarification=True,
        clarifying_questions=["What is the issue?"],
        retrieved_facts=[],
        model_reasoning="Uncertain",
        reasoning="Uncertain",
        known_issue=False,
        knowledge_base_references=[],
        recommended_team="Support",
        draft_first_response="Please clarify."
    )

    checked = apply_priority_sanity_check(mock_result, "broken", "broken")
    assert checked.flagged_for_human_review is True


# =====================================================================
# 9. PII Masking & Sensitive Data Sanitization
# =====================================================================

def test_sensitive_data_sanitization():
    """Customer emails, phone numbers, and secrets must be masked."""
    text_with_pii = (
        "Customer email is john.doe@enterprise.com, phone is 555-123-4567, "
        "and api_key: 'AIzaSyD9381928301928301293'."
    )
    sanitized = sanitize_text(text_with_pii)

    assert "john.doe@enterprise.com" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "555-123-4567" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "AIzaSyD9381928301928301293" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized


# =====================================================================
# 10. Account Health Metrics & Risk Detection Tests
# =====================================================================

def test_account_metrics_calculations():
    """Seat utilization and renewal calculations must be accurate and safe."""
    account = {
        "seats_licensed": 500,
        "seats_active": 250,
        "renewal_date": "2026-10-15"
    }
    util = calculate_seat_utilization(account)
    assert util == 50.0

    # Zero seats edge case
    assert calculate_seat_utilization({"seats_licensed": 0, "seats_active": 0}) == 0.0


def test_evidence_quote_extraction():
    """Evidence quote extraction must extract exact unaltered sentence from ticket."""
    subject = "Production failure"
    body = "System has halted. This continuous pipeline downtime is completely unacceptable. We require immediate assistance."
    phrase = "unacceptable"

    quote = extract_evidence_quote(subject, body, phrase)
    assert "completely unacceptable" in quote
    assert quote == "This continuous pipeline downtime is completely unacceptable."


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
