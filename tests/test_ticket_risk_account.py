import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import (
    load_tickets,
    load_accounts
)


tickets = load_tickets()
accounts = load_accounts()


# Build a set of valid account IDs
valid_account_ids = {

    account["account_id"]

    for account in accounts
}


signals = [

    "switching vendors",
    "switch vendor",
    "competitor",
    "competing vendor",
    "cancel",
    "cancellation",
    "terminate",
    "not renew",
    "won't renew",
    "will not renew",
    "unacceptable",
    "escalate",
    "escalation",
    "executive escalation",
    "business continuity at risk"
]


matches = []


for ticket in tickets:

    # Only use tickets whose account
    # exists in account summaries
    if ticket["account_id"] not in valid_account_ids:

        continue


    text = (
        f"{ticket.get('subject', '')} "
        f"{ticket.get('body', '')}"
    ).lower()


    matched_signals = [

        signal

        for signal in signals

        if signal in text
    ]


    if matched_signals:

        matches.append({

            "ticket_id": ticket[
                "ticket_id"
            ],

            "account_id": ticket[
                "account_id"
            ],

            "subject": ticket[
                "subject"
            ],

            "signals": matched_signals,

            "body": ticket[
                "body"
            ]
        })


print(
    f"\nTOTAL VALID RISK MATCHES: "
    f"{len(matches)}\n"
)


for match in matches[:20]:

    print(
        "=" * 60
    )

    print(
        "TICKET:",
        match["ticket_id"]
    )

    print(
        "ACCOUNT:",
        match["account_id"]
    )

    print(
        "SUBJECT:",
        match["subject"]
    )

    print(
        "SIGNALS:",
        match["signals"]
    )

    print(
        "\nBODY:"
    )

    print(
        match["body"]
    )

    print()