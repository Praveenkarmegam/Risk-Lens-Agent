import json

from src.config import TICKETS_PATH, ACCOUNTS_PATH


def load_tickets():
    """Load all support tickets from tickets.json."""

    with open(TICKETS_PATH, "r", encoding="utf-8") as file:
        tickets = json.load(file)

    return tickets


def load_accounts():
    """Load all customer accounts from accounts.json."""

    with open(ACCOUNTS_PATH, "r", encoding="utf-8") as file:
        accounts = json.load(file)

    return accounts


def get_account_by_id(account_id):
    """Find an account by its account_id."""

    accounts = load_accounts()

    for account in accounts:
        if account["account_id"] == account_id:
            return account

    return None


def get_tickets_by_account(account_id):
    """Return all tickets belonging to an account."""

    tickets = load_tickets()

    return [
        ticket
        for ticket in tickets
        if ticket["account_id"] == account_id
    ]