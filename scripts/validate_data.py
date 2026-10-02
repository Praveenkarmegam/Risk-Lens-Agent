import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_validator import (
    validate_tickets,
    validate_accounts
)


def main():
    ticket_errors = validate_tickets()
    account_errors = validate_accounts()

    print("=" * 50)
    print("DATA VALIDATION SUMMARY")
    print("=" * 50)
    print("Ticket Validation Errors:", len(ticket_errors))
    print("Account Validation Errors:", len(account_errors))

    if ticket_errors:
        print("\nSample Ticket Error:")
        print(ticket_errors[0])

    if account_errors:
        print("\nSample Account Error:")
        print(account_errors[0])

    if not ticket_errors and not account_errors:
        print("\nAll tickets and accounts strictly conform to required schemas.")


if __name__ == "__main__":
    main()
