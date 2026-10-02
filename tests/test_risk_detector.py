import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.loader import (
    get_account_by_id,
    get_last_90_days_tickets
)

from src.account_health.risk_detector import (
    detect_account_risks
)


account_id = "ACC-3336"


account = (
    get_account_by_id(
        account_id
    )
)


tickets = (
    get_last_90_days_tickets(
        account_id
    )
)


risks = (
    detect_account_risks(
        account,
        tickets
    )
)


print("\nDETECTED RISKS\n")

for risk in risks:

    print("----------------")

    for key, value in risk.model_dump().items():

        print(
            f"{key}: {value}"
        )