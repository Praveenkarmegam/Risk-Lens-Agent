import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.account_health.loader import load_accounts


def main():

    accounts = load_accounts()

    open_ticket_values = sorted(
        account.get(
            "open_tickets",
            0
        )
        for account in accounts
    )

    print("\nOPEN TICKET DISTRIBUTION")
    print("-" * 50)

    print(
        "Total Accounts:",
        len(accounts)
    )

    print(
        "Minimum:",
        min(open_ticket_values)
    )

    print(
        "Maximum:",
        max(open_ticket_values)
    )

    print(
        "Sorted Values:"
    )

    print(
        open_ticket_values
    )


    print("\nTOP ACCOUNTS BY OPEN TICKETS")
    print("-" * 50)

    sorted_accounts = sorted(
        accounts,
        key=lambda account: account.get(
            "open_tickets",
            0
        ),
        reverse=True
    )

    for account in sorted_accounts[:10]:

        print(
            account["account_id"],
            "|",
            account["company"],
            "| Open Tickets:",
            account.get(
                "open_tickets"
            ),
            "| Health:",
            account.get(
                "health_status"
            ),
            "| Usage:",
            account.get(
                "usage_trend"
            )
        )


if __name__ == "__main__":

    main()