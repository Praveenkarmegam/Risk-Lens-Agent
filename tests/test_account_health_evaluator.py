import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

from src.evaluation.account_health_cases import (
    get_account_health_test_cases
)

from src.evaluation.account_health_evaluator import (
    evaluate_account_health_case
)


def run_account_health_evaluation():

    test_cases = get_account_health_test_cases()

    results = []

    print("\n")
    print("=" * 60)
    print("ACCOUNT HEALTH EVALUATION")
    print("=" * 60)

    for index, test_case in enumerate(
        test_cases,
        start=1
    ):

        print("\n")

        print(
            f"Running {index}/{len(test_cases)}: "
            f"{test_case['name']}"
        )

        result = evaluate_account_health_case(
            test_case
        )

        results.append(result)

        print(result)

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    total_cases = len(results)

    passed_cases = sum(
        1
        for result in results
        if result["passed"]
    )

    average_quality = round(
        sum(
            result["quality_score"]
            for result in results
        ) / total_cases,
        2
    )

    pass_rate = round(
        passed_cases / total_cases,
        4
    )

    summary = {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "pass_rate": pass_rate,
        "average_quality_score": average_quality,
        "results": results
    }

    print("\n")
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(
        f"Passed: "
        f"{passed_cases}/{total_cases}"
    )

    print(
        f"Pass Rate: "
        f"{pass_rate * 100:.1f}%"
    )

    print(
        f"Average Quality Score: "
        f"{average_quality}"
    )

    # -----------------------------------------
    # Save structured evaluation results
    # -----------------------------------------

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "account_health_eval_results.json"

    with open(
        report_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(summary, file, indent=4)

    print("\n")
    print("Account health evaluation results saved to:")
    print(f"- {report_file}")

    return summary


def main():

    run_account_health_evaluation()


if __name__ == "__main__":

    main()

