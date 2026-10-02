# Evaluation & Audit Reports

This directory stores structured evaluation reports, test benchmarks, and quality audits produced by the RiskLens AI evaluation harness:

1. **`eval_report.json`**:
   - The unified final evaluation report combining Task 1 (Ticket Triage accuracy and schema conformance) and Task 2 (TAM Account Health risk metrics and narrative quality).
   - Produced by: `python run_evaluation.py`

2. **`triage_eval_results.json`**:
   - Case-by-case evaluation results for the 6 triage benchmark test cases (accuracy, category, priority, confidence, and KB reference validation).
   - Produced by: `python scripts/run_triage_evaluation.py`

3. **`account_health_eval_results.json`**:
   - Case-by-case TAM account health evaluation metrics across accounts, assessing ARR calculations, open ticket distributions, risk indicator detection, and qualitative narrative scores.
   - Produced by: `python tests/test_account_health_evaluator.py`
