def calculate_quality_score(checks: dict) -> float:
    """
    Calculate a quality score between 0 and 1
    based on the proportion of acceptance
    criteria that passed.
    """

    if not checks:
        return 0.0

    total_checks = len(checks)

    passed_checks = sum(
        1
        for value in checks.values()
        if value is True
    )

    score = passed_checks / total_checks

    return round(score, 2)


def determine_pass(
    checks: dict,
    minimum_score: float = 0.8
) -> bool:
    """
    Determine whether a test passes.

    A test passes when its quality score
    meets the minimum threshold.
    """

    score = calculate_quality_score(checks)

    return score >= minimum_score


def build_test_result(
    name: str,
    checks: dict,
    details: dict | None = None,
    minimum_score: float = 0.8
) -> dict:
    """
    Build a standardized evaluation result.
    """

    quality_score = calculate_quality_score(
        checks
    )

    passed = determine_pass(
        checks,
        minimum_score
    )

    return {
        "name": name,
        "passed": passed,
        "quality_score": quality_score,
        "checks": checks,
        "details": details or {}
    }