import json


PROMPT_VERSION = "tam_health_v2"


def build_account_health_prompt(
    account,
    metrics,
    risks,
    recent_tickets
):
    """
    Build the prompt for narrative synthesis.

    Risk detection and evidence extraction
    are performed deterministically by Python.
    """

    context = {
        "account": account,
        "metrics": metrics,
        "verified_risks": risks,
        "recent_tickets": recent_tickets
    }

    context_json = json.dumps(
        context,
        indent=2,
        default=str
    )

    return f"""
You are an internal AI assistant for
Technical Account Managers.

Generate only:

1. executive_summary
2. recommended_talking_points

PROMPT VERSION:
{PROMPT_VERSION}

STRICT RULES:

1. Use ONLY the provided data.

2. Do not invent incidents, customer
   sentiment, product problems, metrics,
   commitments, or timelines.

3. The executive summary must contain
   exactly 3 to 5 sentences.

4. Treat account health_status values as
   raw dataset labels. Do not assume that
   a value such as "New" is positive or
   negative unless supported by other
   provided data.

5. Only describe a product-specific issue
   when the provided ticket explicitly
   identifies that product.

6. Do not infer that all products listed
   on the account are affected by a ticket.

7. Use deterministic metrics exactly as
   provided.

8. Do not generate risks, ticket IDs,
   evidence quotes, or flagged issues.

9. If verified_risks contains material
   ticket-level risks, reflect the
   underlying issue in the executive
   summary when relevant.

10. Recommended talking points must be
    specific and actionable for the TAM.

11. If days_until_renewal is positive,
    you may describe the renewal as
    upcoming.

12. If days_until_renewal is zero or
    negative, do not describe the renewal
    as upcoming.

13. Do not invent commitments such as
    guaranteed fixes, timelines, or
    product roadmap promises.

14. Do not assume that a product mentioned
    in a ticket belongs to the account's
    product list unless both data sources
    explicitly support it.

OUTPUT REQUIREMENTS:

Return only valid JSON matching this structure:

{{
    "executive_summary": "3 to 5 sentences",
    "recommended_talking_points": [
        "Actionable TAM talking point",
        "Actionable TAM talking point"
    ]
}}

INPUT DATA:

{context_json}
"""