import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.account_health_cases import (
    get_account_health_test_cases
)


cases = get_account_health_test_cases()


print(
    f"\nTOTAL CASES: {len(cases)}\n"
)


for index, case in enumerate(
    cases,
    start=1
):

    print(
        f"{index}. {case['name']}"
    )

    print(
        f"   Account: {case['account_id']}"
    )

    print(
        f"   Expected: {case['expected']}"
    )

    print()