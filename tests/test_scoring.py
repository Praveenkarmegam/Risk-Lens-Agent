import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.scoring import (
    build_test_result
)


checks = {
    "account_found": True,
    "summary_length": True,
    "risks_present": True,
    "talking_points": False,
    "deterministic": True
}


result = build_test_result(
    name="Scoring System Test",
    checks=checks
)


print(result)