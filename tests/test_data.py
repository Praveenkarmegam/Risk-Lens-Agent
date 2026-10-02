import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import (
    load_tickets,
    load_accounts,
    get_account_by_id,
    get_tickets_by_account
)


tickets = load_tickets()
accounts = load_accounts()


print("Total Tickets:", len(tickets))
print("Total Accounts:", len(accounts))


print("\nFirst Ticket:")
print(tickets[0])


print("\nFirst Account:")
print(accounts[0])


# Test account lookup
account_id = accounts[0]["account_id"]

account = get_account_by_id(account_id)

print("\nAccount Lookup:")
print(account)


# Test account ticket lookup
account_tickets = get_tickets_by_account(account_id)

print("\nTickets for account:", account_id)
print("Count:", len(account_tickets))