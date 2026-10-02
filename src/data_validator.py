from src.data_loader import load_tickets, load_accounts


REQUIRED_TICKET_FIELDS = [
    "ticket_id",
    "account_id",
    "company",
    "subject",
    "body",
    "product",
    "product_area",
    "category",
    "urgency",
    "status",
    "created_at"
]


REQUIRED_ACCOUNT_FIELDS = [
    "account_id",
    "company",
    "tam",
    "plan_tier",
    "arr_usd",
    "products",
    "health_status",
    "usage_trend",
    "open_tickets",
    "renewal_date"
]


def validate_tickets():
    tickets = load_tickets()

    missing_fields = []

    for ticket in tickets:
        for field in REQUIRED_TICKET_FIELDS:

            if field not in ticket:
                missing_fields.append(
                    {
                        "ticket_id": ticket.get("ticket_id", "UNKNOWN"),
                        "missing_field": field
                    }
                )

    return missing_fields


def validate_accounts():
    accounts = load_accounts()

    missing_fields = []

    for account in accounts:
        for field in REQUIRED_ACCOUNT_FIELDS:

            if field not in account:
                missing_fields.append(
                    {
                        "account_id": account.get("account_id", "UNKNOWN"),
                        "missing_field": field
                    }
                )

    return missing_fields