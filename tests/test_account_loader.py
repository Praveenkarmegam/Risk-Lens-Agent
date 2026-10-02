import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import (
    load_accounts
)

from src.account_health.loader import (
    get_account_by_id,
    get_account_tickets,
    get_last_90_days_tickets
)


accounts = load_accounts()


# Pick first account
account_id = accounts[0][
    "account_id"
]


print(
    "\nACCOUNT ID:",
    account_id
)


# --------------------------------
# Account
# --------------------------------

account = get_account_by_id(
    account_id
)

print("\nACCOUNT")

print(account)


# --------------------------------
# All Tickets
# --------------------------------

all_tickets = (
    get_account_tickets(
        account_id
    )
)

print(
    "\nTOTAL ACCOUNT TICKETS:",
    len(all_tickets)
)


# --------------------------------
# Last 90 Days
# --------------------------------

recent_tickets = (
    get_last_90_days_tickets(
        account_id
    )
)

print(
    "\nLAST 90 DAYS TICKETS:",
    len(recent_tickets)
)


for ticket in recent_tickets[:5]:

    print("\n----------------")

    print(
        "Ticket:",
        ticket["ticket_id"]
    )

    print(
        "Created:",
        ticket["created_at"]
    )

    print(
        "Subject:",
        ticket["subject"]
    )