import json
import re
from typing import List, Dict, Any, Optional
from google.genai import types

from src.config import GEMINI_MODEL, is_gemini_configured
from src.gemini_client import get_gemini_client, generate_with_retry
from src.triage.schemas import (
    TicketTriageResult,
    KnowledgeBaseReference,
    IssueCategory,
    Priority,
    ConfidenceLevel,
)
from src.triage.validators import apply_priority_sanity_check
from src.triage.prompts import build_triage_prompt
from src.utils.sanitizer import safe_log_warning, safe_log_error, safe_log_info


def format_kb_context(retrieval_results: List[Dict[str, Any]]) -> str:
    """Convert retrieved KB chunks into structured context for Gemini."""
    if not retrieval_results:
        return ""

    context_parts = []
    for index, result in enumerate(retrieval_results, start=1):
        context_parts.append(
            f"KB RESULT {index}\n"
            f"Document: {result.get('document', '')}\n"
            f"Path: {result.get('path', '')}\n"
            f"Section: {result.get('section', 'General')}\n"
            f"Retrieval Score: {result.get('score', 0.0)}\n\n"
            f"Content:\n{result.get('content', '')}\n"
            f"----------------------------------------"
        )
    return "\n".join(context_parts)


def extract_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from model output, handling markdown code fences,
    extraneous commentary, and common formatting artifacts.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Model output is empty")

    text = raw_text.strip()

    # 1. Strip markdown fences if present
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    # 2. Extract outermost JSON object
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    # 3. Clean common JSON issues (trailing commas before closing brackets)
    text = re.sub(r",\s*([\]}])", r"\1", text)

    return json.loads(text)


def compute_confidence_score(
    retrieval_results: List[Dict[str, Any]],
    model_confidence: str,
    needs_clarification: bool,
    subject: str,
    body: str
) -> float:
    """
    Calculate a calibrated numeric confidence score between 0.0 and 1.0.
    Factors in retrieval quality, model self-assessment, and ticket completeness.
    """
    if needs_clarification:
        return 0.35

    ticket_text = f"{subject} {body}".strip()
    if len(ticket_text) < 40:
        return 0.40

    # Base from model declared level
    base_scores = {
        "High": 0.85,
        "Medium": 0.70,
        "Low": 0.45
    }
    score = base_scores.get(model_confidence, 0.70)

    # Retrieval bonus: if top KB match has strong score (>0.5), boost confidence
    if retrieval_results:
        top_kb_score = float(retrieval_results[0].get("score", 0.0))
        if top_kb_score >= 0.50:
            score = min(0.98, score + 0.08)
        elif top_kb_score < 0.15:
            score = max(0.50, score - 0.08)

    return round(score, 2)


def generate_deterministic_fallback(
    subject: str,
    body: str,
    retrieval_results: List[Dict[str, Any]],
    reason: str
) -> TicketTriageResult:
    """
    Construct a safe, valid fallback result when the Gemini API is unavailable,
    quota is exhausted, or model output is malformed. Ensures zero downtime.
    """
    ticket_text = f"{subject} {body}".lower()

    # Default values
    category: IssueCategory = "Other"
    priority: Priority = "P3"
    product_area = "General"
    recommended_team = "Technical Support"
    needs_clarification = False
    clarifying_questions: List[str] = []

    # Deterministic heuristics
    if any(s in ticket_text for s in ["outage", "down", "completely unavailable", "workflows have stopped"]):
        category = "Incident"
        priority = "P1"
        product_area = "Platform Availability"
        recommended_team = "Incident Response & Platform Operations"
    elif any(s in ticket_text for s in ["sso", "login", "saml", "authentication", "password"]):
        category = "Authentication"
        priority = "P2"
        product_area = "Authentication"
        recommended_team = "Identity & Access Support"
    elif any(s in ticket_text for s in ["slow", "performance", "timeout", "latency"]):
        category = "Performance"
        priority = "P2"
        product_area = "Performance"
        recommended_team = "Performance Engineering"
    elif any(s in ticket_text for s in ["feature request", "request:", "bulk archive", "add support for"]):
        category = "Feature Request"
        priority = "P3"
        product_area = "Data Management"
        recommended_team = "Product Management"
    elif any(s in ticket_text for s in ["how do i", "how to", "settings", "configure"]):
        category = "How-to"
        priority = "P4"
        product_area = "User Settings"
        recommended_team = "Customer Support"
    elif len(ticket_text) < 40 or any(ticket_text.startswith(v) for v in ["not working", "broken", "help"]):
        needs_clarification = True
        clarifying_questions = [
            "Which product or component is experiencing this problem?",
            "What error message or behavior are you observing?"
        ]
        priority = "P3"

    kb_refs: List[KnowledgeBaseReference] = []
    if retrieval_results:
        top_match = retrieval_results[0]
        if top_match.get("score", 0) >= 0.20:
            kb_refs.append(
                KnowledgeBaseReference(
                    document=top_match["document"],
                    path=top_match["path"],
                    relevance_reason="Relevant documentation identified for ticket keywords."
                )
            )

    return TicketTriageResult(
        product_area=product_area,
        issue_category=category,
        priority=priority,
        confidence="Low",
        confidence_score=0.40,
        needs_clarification=needs_clarification,
        clarifying_questions=clarifying_questions,
        retrieved_facts=[f"KB reference found: {kb_refs[0].document}"] if kb_refs else [],
        model_reasoning=f"Fallback triage applied: {reason}",
        reasoning=f"Automated classification based on deterministic keyword matching ({reason}).",
        known_issue=False,
        knowledge_base_references=kb_refs,
        recommended_team=recommended_team,
        draft_first_response=(
            f"Thank you for reaching out. We have received your inquiry regarding '{subject}' "
            f"and our {recommended_team} is reviewing the details to provide next steps."
        ),
        audit_notes=f"Deterministic fallback executed. Reason: {reason}",
        flagged_for_human_review=True
    )


def triage_ticket(
    subject: str,
    body: str,
    retriever,
    top_k: int = 3
) -> TicketTriageResult:
    """
    Perform complete ticket triage:
    1. Knowledge Base Retrieval
    2. Gemini prompt synthesis
    3. Structured JSON generation
    4. Pydantic validation and error recovery
    5. Deterministic priority guardrails
    6. Calibrated confidence scoring and audit trail generation
    """
    subject_clean = (subject or "").strip()
    body_clean = (body or "").strip()
    search_query = f"{subject_clean}\n{body_clean}".strip()

    # 1. Retrieve KB context
    retrieval_results = []
    if retriever:
        try:
            retrieval_results = retriever.search(query=search_query, top_k=top_k)
        except Exception as e:
            safe_log_warning(f"KB retrieval exception: {e}")

    kb_context = format_kb_context(retrieval_results)

    # 2. Check if Gemini client can be initialized
    result: Optional[TicketTriageResult] = None

    if is_gemini_configured():
        try:
            client = get_gemini_client()
            prompt = build_triage_prompt(
                subject=subject_clean,
                body=body_clean,
                kb_context=kb_context
            )

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TicketTriageResult,
                temperature=0.1,
                top_p=0.95
            )

            response = generate_with_retry(
                client=client,
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )

            raw_text = getattr(response, "text", "") or ""
            parsed_data = extract_and_parse_json(raw_text)
            result = TicketTriageResult.model_validate(parsed_data)

        except Exception as api_err:
            safe_log_warning(f"Gemini API or validation error in triage: {api_err}. Falling back to deterministic rules.")
            result = generate_deterministic_fallback(
                subject=subject_clean,
                body=body_clean,
                retrieval_results=retrieval_results,
                reason=f"Gemini error: {api_err}"
            )
    else:
        safe_log_info("GEMINI_API_KEY not configured. Using deterministic triage fallback.")
        result = generate_deterministic_fallback(
            subject=subject_clean,
            body=body_clean,
            retrieval_results=retrieval_results,
            reason="GEMINI_API_KEY not configured"
        )

    # 3. Apply Priority and Ambiguity Guardrails
    result = apply_priority_sanity_check(
        result=result,
        subject=subject_clean,
        body=body_clean,
        retrieval_results=retrieval_results
    )

    # 4. Calibrate confidence score
    result.confidence_score = compute_confidence_score(
        retrieval_results=retrieval_results,
        model_confidence=result.confidence,
        needs_clarification=result.needs_clarification,
        subject=subject_clean,
        body=body_clean
    )

    # Ensure confidence bucket matches confidence_score
    if result.confidence_score >= 0.80:
        result.confidence = "High"
    elif result.confidence_score >= 0.50:
        result.confidence = "Medium"
    else:
        result.confidence = "Low"

    # 5. Populate audit notes
    kb_info = f"KB chunks retrieved: {len(retrieval_results)}"
    if retrieval_results:
        top_score = retrieval_results[0].get("score", 0.0)
        kb_info += f" (top score: {top_score})"

    audit_entry = (
        f"Triage processed. {kb_info}. Priority: {result.priority}. "
        f"Confidence: {result.confidence} ({result.confidence_score}). "
        f"Human review: {result.flagged_for_human_review}."
    )
    result.audit_notes = f"{result.audit_notes} | {audit_entry}" if result.audit_notes else audit_entry

    return result