from src.account_health.service import (
    generate_account_health_brief
)


def evaluate_account_health_case(test_case):
    """
    Evaluate one account health test case.

    Returns:
        {
            name,
            passed,
            quality_score,
            checks,
            details
        }
    """

    account_id = test_case["account_id"]

    expected = test_case["expected"]

    checks = {}


    try:

        # -----------------------------------------
        # Generate account health brief
        # -----------------------------------------

        result = generate_account_health_brief(
            account_id=account_id
        )


        # -----------------------------------------
        # Convert Pydantic model to dictionary
        # -----------------------------------------

        if hasattr(result, "model_dump"):

            result = result.model_dump()

        elif hasattr(result, "dict"):

            result = result.dict()


        # -----------------------------------------
        # Basic validation
        # -----------------------------------------

        checks["account_found"] = (
            result is not None
        )


        # -----------------------------------------
        # Executive summary validation
        # -----------------------------------------

        summary = result.get(
            "executive_summary",
            ""
        )

        if expected.get("has_executive_summary", True):
            checks[
                "has_executive_summary"
            ] = (
                isinstance(summary, str)
                and len(summary.strip()) > 20
            )


        # -----------------------------------------
        # Risks validation
        # -----------------------------------------

        risks = result.get(
            "open_risks_and_flagged_issues",
            []
        )

        if expected.get("has_risks"):
            checks["has_risks"] = (
                isinstance(risks, list)
                and len(risks) > 0
            )


        # -----------------------------------------
        # Talking points validation
        # -----------------------------------------

        talking_points = result.get(
            "recommended_talking_points",
            []
        )

        if expected.get("has_talking_points", True):
            checks[
                "has_talking_points"
            ] = (
                isinstance(talking_points, list)
                and len(talking_points) > 0
            )


        # -----------------------------------------
        # At Risk signal
        # -----------------------------------------

        if expected.get(
            "at_risk_signal_detected"
        ):

            checks[
                "at_risk_signal_detected"
            ] = any(

                risk.get("risk_type")
                == "Account Health"

                and

                risk.get("severity")
                == "High"

                for risk in risks

            )


        # -----------------------------------------
        # Usage decline signal
        # -----------------------------------------

        if expected.get(
            "usage_decline_detected"
        ):

            checks[
                "usage_decline_detected"
            ] = any(

                risk.get("risk_type")
                == "Usage Decline"

                for risk in risks

            )


        # -----------------------------------------
        # Ticket context
        # -----------------------------------------

        if expected.get(
            "ticket_context_present"
        ):

            checks[
                "ticket_context_present"
            ] = (

                "ticket" in summary.lower()

                or

                any(
                    risk.get("source") == "ticket"
                    for risk in risks
                )

            )


        # -----------------------------------------
        # Account identity
        # -----------------------------------------

        if expected.get(
            "account_identity_correct"
        ):

            checks[
                "account_identity_correct"
            ] = (
                result.get("account_id")
                == account_id
            )


        # -----------------------------------------
        # Ticket-level risk
        # -----------------------------------------

        if expected.get(
            "has_ticket_risk"
        ):

            ticket_risks = [

                risk

                for risk in risks

                if risk.get("source")
                == "ticket"

            ]

            checks[
                "has_ticket_risk"
            ] = (
                len(ticket_risks) > 0
            )


        # -----------------------------------------
        # Evidence quote
        # -----------------------------------------

        if expected.get(
            "evidence_quote_present"
        ):

            ticket_risks = [

                risk

                for risk in risks

                if risk.get("source")
                == "ticket"

            ]

            checks[
                "evidence_quote_present"
            ] = any(

                isinstance(
                    risk.get(
                        "evidence_quote"
                    ),
                    str
                )

                and

                len(
                    risk.get(
                        "evidence_quote"
                    ).strip()
                ) > 0

                for risk in ticket_risks

            )


        # -----------------------------------------
        # Calculate score
        # -----------------------------------------

        total_checks = len(
            checks
        )

        passed_checks = sum(
            checks.values()
        )

        quality_score = round(
            passed_checks / total_checks,
            2
        )


        # -----------------------------------------
        # Overall result
        # -----------------------------------------

        passed = all(
            checks.values()
        )


        return {

            "name": test_case[
                "name"
            ],

            "passed": passed,

            "quality_score": (
                quality_score
            ),

            "checks": checks,

            "details": {
                "account_id": account_id
            }

        }


    # =============================================
    # Error handling
    # =============================================

    except Exception as error:

        error_message = str(
            error
        )


        # -----------------------------------------
        # Adversarial missing-account validation
        # -----------------------------------------

        if expected.get(
            "raises_clear_error"
        ):

            checks[
                "raises_clear_error"
            ] = (
                "account not found"
                in error_message.lower()
            )


            return {

                "name": test_case[
                    "name"
                ],

                "passed": checks[
                    "raises_clear_error"
                ],

                "quality_score": (

                    1.0

                    if checks[
                        "raises_clear_error"
                    ]

                    else 0.0

                ),

                "checks": checks,

                "details": {
                    "error": error_message
                }

            }


        # -----------------------------------------
        # Unexpected execution failure
        # -----------------------------------------

        return {

            "name": test_case[
                "name"
            ],

            "passed": False,

            "quality_score": 0.0,

            "checks": {
                "execution": False
            },

            "details": {
                "error": error_message
            }

        }