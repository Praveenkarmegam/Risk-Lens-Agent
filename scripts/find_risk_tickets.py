import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_tickets


def main():
    tickets = load_tickets()

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
        "legal"
    ]

    matches = []

    for ticket in tickets:
        subject = ticket.get("subject", "")
        body = ticket.get("body", "")
        text = f"{subject} {body}".lower()

        matched_signals = [signal for signal in signals if signal in text]

        if matched_signals:
            matches.append({
                "ticket_id": ticket.get("ticket_id"),
                "account_id": ticket.get("account_id"),
                "subject": subject,
                "signals": matched_signals,
                "body": body
            })

    print(f"\nTOTAL RISK TICKET MATCHES: {len(matches)}\n")

    for match in matches:
        print("=" * 70)
        print(f"TICKET: {match['ticket_id']}")
        print(f"ACCOUNT: {match['account_id']}")
        print(f"SUBJECT: {match['subject']}")
        print(f"SIGNALS: {', '.join(match['signals'])}")
        print("\nBODY:")
        print(match["body"])
        print()


if __name__ == "__main__":
    main()
