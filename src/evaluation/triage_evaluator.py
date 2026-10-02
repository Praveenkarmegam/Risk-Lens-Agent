def evaluate_triage_result(
    test_case,
    result
):
    """
    Evaluate one triage result against
    expected acceptance criteria.
    """

    checks = {}


    # -----------------------------
    # Category Check
    # -----------------------------

    expected_category = (
        test_case.get(
            "expected_category"
        )
    )

    if expected_category is None:

        checks["category"] = True

    else:

        checks["category"] = (
            result.issue_category
            == expected_category
        )


    # -----------------------------
    # Priority Check
    # -----------------------------

    allowed_priorities = (
        test_case[
            "allowed_priorities"
        ]
    )

    checks["priority"] = (
        result.priority
        in allowed_priorities
    )


    # -----------------------------
    # Schema Checks
    # -----------------------------

    checks["reasoning"] = bool(
        result.reasoning.strip()
    )

    checks["recommended_team"] = bool(
        result.recommended_team.strip()
    )

    checks["draft_response"] = bool(
        result.draft_first_response.strip()
    )
    
    checks["confidence"] = (
        result.confidence
        in ["High", "Medium", "Low"]
    )
    
    checks["clarification_schema"] = (
        isinstance(
        result.needs_clarification,
        bool
    )
    and isinstance(
        result.clarifying_questions,
        list
    )
    )


    # -----------------------------
    # Final Score
    # -----------------------------

    passed = all(
        checks.values()
    )

    return {
        "name": test_case["name"],
        "passed": passed,
        "checks": checks,
        "predicted_category": (
            result.issue_category
        ),
        "predicted_priority": (
            result.priority
        ),
         "confidence": (
            result.confidence
        ),
        "needs_clarification": (
            result.needs_clarification
        )
    }