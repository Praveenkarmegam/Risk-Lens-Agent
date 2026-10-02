# Utility Scripts

This directory contains developer and operational utilities for dataset inspection, validation, and API connectivity:

1. **`validate_data.py`**:
   - Validates all records in `data_risklens/tickets.json` and `data_risklens/accounts.json` against required schema fields.
   - Run: `python scripts/validate_data.py`

2. **`find_risk_tickets.py`**:
   - Scans ticket bodies and subjects for critical risk indicators (churn, cancellation, vendor switching, escalation language).
   - Run: `python scripts/find_risk_tickets.py`

3. **`list_models.py`**:
   - Queries the Google GenAI client to list all Gemini models available to the current API key.
   - Run: `python scripts/list_models.py`

4. **`run_triage_evaluation.py`**:
   - Executes the automated 6-case ticket triage benchmark suite (Task 1) and generates structured JSON output in `reports/triage_eval_results.json`.
   - Run: `python scripts/run_triage_evaluation.py`

