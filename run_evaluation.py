import json
import subprocess
import sys

from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)


def run_script(script_name):

    print("\n")
    print("=" * 70)
    print(f"RUNNING: {script_name}")
    print("=" * 70)

    script_path = BASE_DIR / script_name
    if not script_path.exists():
        script_path = BASE_DIR / "scripts" / script_name
    if not script_path.exists():
        script_path = BASE_DIR / "tests" / script_name

    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)

    process = subprocess.run(
        [
            sys.executable,
            str(script_path)
        ],
        capture_output=True,
        text=True,
        env=env
    )

    print(process.stdout)

    if process.stderr:

        print("STDERR:")
        print(process.stderr)

    return process.returncode


def load_json(filename):

    file_path = BASE_DIR / filename
    if not file_path.exists():
        file_path = BASE_DIR / "reports" / filename

    if not file_path.exists():

        raise FileNotFoundError(
            f"Evaluation result file not found: "
            f"{filename}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_evaluation_summary(data):

    """
    Normalize different possible evaluation JSON formats.

    Supported formats:

    1. Dictionary:
       {
           "total_cases": 10,
           "passed_cases": 10,
           "results": [...]
       }

    2. Dictionary:
       {
           "results": [...]
       }

    3. Dictionary:
       {
           "evaluation_results": [...]
       }

    4. Dictionary:
       {
           "cases": [...]
       }

    5. Plain list:
       [
           {
               "passed": true
           }
       ]
    """

    # ------------------------------------------
    # Case 1: JSON root is a list
    # ------------------------------------------

    if isinstance(data, list):

        results = data

    # ------------------------------------------
    # Case 2: JSON root is a dictionary
    # ------------------------------------------

    elif isinstance(data, dict):

        results = data.get(
            "results",
            data.get(
                "evaluation_results",
                data.get(
                    "cases",
                    []
                )
            )
        )

    # ------------------------------------------
    # Invalid / unknown format
    # ------------------------------------------

    else:

        results = []

    # Safety check
    if not isinstance(results, list):

        results = []

    # ------------------------------------------
    # Calculate totals from actual cases
    # ------------------------------------------

    total_cases = len(results)

    passed_cases = sum(
        1
        for result in results
        if isinstance(result, dict)
        and result.get("passed") is True
    )

    pass_rate = (
        round(
            (
                passed_cases
                / total_cases
            )
            * 100,
            1
        )
        if total_cases > 0
        else 0.0
    )

    return {

        "total_cases": total_cases,

        "passed_cases": passed_cases,

        "pass_rate": pass_rate,

        "results": results
    }


def main():

    print("\n")
    print("=" * 70)
    print(
        "AI SUPPORT & TAM PLATFORM — "
        "EVALUATION HARNESS"
    )
    print("=" * 70)

    # ------------------------------------------
    # Run Task 1
    # ------------------------------------------

    triage_return_code = run_script(
        "run_triage_evaluation.py"
    )

    # ------------------------------------------
    # Run Task 2
    # ------------------------------------------

    account_return_code = run_script(
        "test_account_health_evaluator.py"
    )

    # ------------------------------------------
    # Load structured results
    # ------------------------------------------

    triage_results = load_json(
        "triage_eval_results.json"
    )

    account_health_results = load_json(
        "account_health_eval_results.json"
    )

    # ------------------------------------------
    # Normalize results
    # ------------------------------------------

    triage_summary = get_evaluation_summary(
        triage_results
    )

    account_health_summary = get_evaluation_summary(
        account_health_results
    )

    # ------------------------------------------
    # Extract normalized values
    # ------------------------------------------

    triage_total = triage_summary[
        "total_cases"
    ]

    triage_passed_cases = triage_summary[
        "passed_cases"
    ]

    account_total = account_health_summary[
        "total_cases"
    ]

    account_passed_cases = account_health_summary[
        "passed_cases"
    ]

    # ------------------------------------------
    # Determine status
    # ------------------------------------------

    triage_status = (
        "PASS"
        if (
            triage_return_code == 0
            and triage_total > 0
            and triage_passed_cases == triage_total
        )
        else "FAIL"
    )

    account_health_status = (
        "PASS"
        if (
            account_return_code == 0
            and account_total > 0
            and account_passed_cases == account_total
        )
        else "FAIL"
    )

    overall_passed = (
        triage_status == "PASS"
        and account_health_status == "PASS"
    )

    # ------------------------------------------
    # Build final report
    # ------------------------------------------

    report = {

        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "overall_status": (
            "PASS"
            if overall_passed
            else "FAIL"
        ),

        "task_1_ticket_triage": {

            "status": triage_status,

            "total_cases": triage_total,

            "passed_cases": triage_passed_cases,

            "pass_rate": triage_summary[
                "pass_rate"
            ],

            "results": triage_summary[
                "results"
            ]
        },

        "task_2_account_health": {

            "status": account_health_status,

            "total_cases": account_total,

            "passed_cases": account_passed_cases,

            "pass_rate": account_health_summary[
                "pass_rate"
            ],

            "average_quality_score": (
                account_health_results.get(
                    "average_quality_score",
                    0
                )
                if isinstance(
                    account_health_results,
                    dict
                )
                else 0
            ),

            "results": account_health_summary[
                "results"
            ]
        }
    }

    # ------------------------------------------
    # Save final report
    # ------------------------------------------

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / "eval_report.json"

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    # ------------------------------------------
    # Print final summary
    # ------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL EVALUATION RESULT")
    print("=" * 70)

    print(
        "Task 1 - Ticket Triage:",
        report[
            "task_1_ticket_triage"
        ]["status"]
    )

    print(
        "Task 1 Cases:",
        f"{triage_passed_cases}/"
        f"{triage_total}"
    )

    print(
        "Task 2 - Account Health:",
        report[
            "task_2_account_health"
        ]["status"]
    )

    print(
        "Task 2 Cases:",
        f"{account_passed_cases}/"
        f"{account_total}"
    )

    print(
        "Task 2 Average Quality:",
        report[
            "task_2_account_health"
        ][
            "average_quality_score"
        ]
    )

    print(
        "\nOverall:",
        report[
            "overall_status"
        ]
    )

    print("\n")

    print(
        "Evaluation report saved to:"
    )

    print(
        report_path.name
    )


if __name__ == "__main__":

    main()