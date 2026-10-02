import json
import re
from typing import Optional
from google.genai import types

from src.config import GEMINI_MODEL, is_gemini_configured
from src.gemini_client import get_gemini_client, generate_with_retry
from src.account_health.loader import (
    get_account_by_id,
    get_last_90_days_tickets,
    get_dataset_reference_date,
)
from src.account_health.analyzer import build_account_metrics
from src.account_health.risk_detector import detect_account_risks
from src.account_health.prompts import build_account_health_prompt
from src.account_health.schemas import (
    AccountHealthBrief,
    AccountHealthNarrative,
    FlaggedIssue,
)
from src.utils.sanitizer import safe_log_warning, safe_log_info


def extract_and_parse_narrative(raw_text: str) -> AccountHealthNarrative:
    """Extract and validate narrative JSON from Gemini output."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Gemini returned an empty narrative response.")

    text = raw_text.strip()
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        text = code_block_match.group(1).strip()

    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]

    data = json.loads(text)
    return AccountHealthNarrative.model_validate(data)


def generate_fallback_narrative(
    account: dict,
    metrics: dict,
    risks: list
) -> AccountHealthNarrative:
    """
    Construct a deterministic executive summary and talking points
    based directly on verified account data when LLM generation is unavailable.
    """
    company = account.get("company", "The account")
    plan = account.get("plan_tier", "Enterprise")
    arr = account.get("arr_usd", 0)
    health = account.get("health_status", "Healthy")
    usage = account.get("usage_trend", "Active")
    open_tickets = account.get("open_tickets", 0)
    p1_tickets = account.get("p1_tickets_last_30d", 0)
    seat_util = metrics.get("seat_utilization_percent", 0.0)

    # 3-5 sentences summary
    sentences = [
        f"{company} is currently on the {plan} tier with an annual recurring revenue of ${arr:,.0f} and an overall health status of '{health}'.",
        f"The account demonstrates an '{usage}' usage trend with a licensed seat utilization of {seat_util}%.",
        f"There are currently {open_tickets} open support tickets on record, with {p1_tickets} critical P1 incidents logged in the past 30 days.",
    ]
    if risks:
        top_risk_types = ", ".join(sorted(list({r.risk_type for r in risks}))[:2])
        sentences.append(f"Key operational risk factors identified for proactive TAM engagement include {top_risk_types}.")
    else:
        sentences.append("The account is operating stably with no acute escalations or churn indicators detected.")

    executive_summary = " ".join(sentences)

    talking_points = []
    if health == "At Risk" or p1_tickets > 0:
        talking_points.append(f"Review root-cause analysis and operational stability post-{p1_tickets} recent critical incidents.")
    if seat_util < 50.0:
        talking_points.append(f"Discuss user onboarding and adoption enablement to improve current seat utilization ({seat_util}%).")
    if open_tickets >= 5:
        talking_points.append(f"Review resolution progress and SLA commitments across the {open_tickets} open support tickets.")
    if not talking_points:
        talking_points.append("Conduct scheduled quarterly operational review and verify satisfaction with current platform performance.")
        talking_points.append("Explore upcoming roadmap capabilities aligned with active product usage.")

    return AccountHealthNarrative(
        executive_summary=executive_summary,
        recommended_talking_points=talking_points
    )


def generate_account_health_brief(account_id: str) -> AccountHealthBrief:
    """
    Generate a TAM account health brief combining:
    1. Deterministic data loading and validation
    2. Deterministic metrics calculation
    3. Deterministic risk and evidence quote detection
    4. Structured executive summary and actionable talking points synthesis
    """
    clean_id = str(account_id).strip()

    # 1. Load account (strictly raise ValueError if not found)
    account = get_account_by_id(clean_id)
    if account is None:
        raise ValueError(f"Account not found: {clean_id}")

    # 2. Load recent tickets
    recent_tickets = get_last_90_days_tickets(clean_id)

    # 3. Deterministic reference date
    reference_date = get_dataset_reference_date()

    # 4. Deterministic metrics
    metrics = build_account_metrics(
        account=account,
        recent_tickets=recent_tickets,
        reference_date=reference_date
    )

    # 5. Deterministic risk detection
    risks = detect_account_risks(
        account=account,
        tickets=recent_tickets
    )

    # 6. Narrative synthesis
    narrative: Optional[AccountHealthNarrative] = None

    if is_gemini_configured():
        try:
            prompt = build_account_health_prompt(
                account=account,
                metrics=metrics,
                risks=risks,
                recent_tickets=recent_tickets
            )

            client = get_gemini_client()
            response = generate_with_retry(
                client=client,
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    top_p=1.0,
                    seed=42,
                    response_mime_type="application/json",
                    response_schema=AccountHealthNarrative
                )
            )

            raw_text = getattr(response, "text", "") or ""
            narrative = extract_and_parse_narrative(raw_text)

        except Exception as err:
            safe_log_warning(f"Gemini narrative generation error: {err}. Using deterministic fallback.")
            narrative = generate_fallback_narrative(account, metrics, risks)
    else:
        safe_log_info("GEMINI_API_KEY not configured. Generating deterministic narrative fallback.")
        narrative = generate_fallback_narrative(account, metrics, risks)

    # Convert detected risks
    verified_risks = [
        FlaggedIssue.model_validate(risk)
        for risk in risks
    ]

    return AccountHealthBrief(
        account_id=account["account_id"],
        company=account["company"],
        executive_summary=narrative.executive_summary,
        open_risks_and_flagged_issues=verified_risks,
        recommended_talking_points=narrative.recommended_talking_points
    )