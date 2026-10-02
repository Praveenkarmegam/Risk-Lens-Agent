import json
import sys
from pathlib import Path

# Ensure project root is in sys.path for standalone script execution
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.kb_loader import load_knowledge_base
from src.retrieval.chunker import create_chunks
from src.retrieval.retriever import KnowledgeBaseRetriever
from src.triage.service import triage_ticket
from src.evaluation.triage_cases import TRIAGE_TEST_CASES
from src.evaluation.triage_evaluator import evaluate_triage_result


def run_triage_evaluation():
    # --------------------------------
    # Build retriever once
    # --------------------------------
    documents = load_knowledge_base()
    chunks = create_chunks(documents)
    retriever = KnowledgeBaseRetriever(chunks)

    # --------------------------------
    # Run test cases
    # --------------------------------
    evaluation_results = []

    for index, test_case in enumerate(TRIAGE_TEST_CASES, start=1):
        print(f"\nRunning {index}/{len(TRIAGE_TEST_CASES)}: {test_case['name']}")

        result = triage_ticket(
            subject=test_case["subject"],
            body=test_case["body"],
            retriever=retriever
        )

        evaluation = evaluate_triage_result(
            test_case=test_case,
            result=result
        )

        evaluation_results.append(evaluation)
        print(json.dumps(evaluation, indent=2))

    # --------------------------------
    # Summary
    # --------------------------------
    total = len(evaluation_results)
    passed = sum(1 for item in evaluation_results if item["passed"])
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

    summary = {
        "total_cases": total,
        "passed_cases": passed,
        "pass_rate": pass_rate,
        "results": evaluation_results
    }

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Pass Rate: {pass_rate}%")

    # --------------------------------
    # Save structured evaluation result
    # --------------------------------
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "triage_eval_results.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)

    print("\nTriage evaluation results saved to:")
    print(f"- {report_file}")
    return summary


def main():
    run_triage_evaluation()


if __name__ == "__main__":
    main()
