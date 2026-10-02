import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.loader import (
    get_account_by_id,
    get_last_90_days_tickets,
    get_dataset_reference_date
)

from src.account_health.analyzer import (
    build_account_metrics
)


account_id = "ACC-3336"


account = get_account_by_id(
    account_id
)


recent_tickets = (
    get_last_90_days_tickets(
        account_id
    )
)


reference_date = (
    get_dataset_reference_date()
)


metrics = (
    build_account_metrics(
        account=account,
        recent_tickets=recent_tickets,
        reference_date=reference_date
    )
)


print(
    "\nDATASET REFERENCE DATE:"
)

print(
    reference_date
)


print(
    "\nACCOUNT METRICS:"
)


for key, value in metrics.items():

    print(
        f"{key}: {value}"
    )