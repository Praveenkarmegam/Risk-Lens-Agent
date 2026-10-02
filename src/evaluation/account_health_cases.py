from src.account_health.loader import load_accounts


def get_first_matching_account(accounts, condition, excluded_ids):
    """
    Return the first account matching the condition
    that has not already been used.
    """
    for account in accounts:
        account_id = account.get("account_id")

        if (
            account_id not in excluded_ids
            and condition(account)
        ):
            return account

    return None


def get_remaining_accounts(accounts, used_account_ids):
    """Return accounts that have not already been selected."""
    return [
        account
        for account in accounts
        if account.get("account_id") not in used_account_ids
    ]


def add_case(cases, used_account_ids, name, account, expected):
    """Add a normal account test case and mark the account as used."""
    if not account:
        return

    account_id = account.get("account_id")

    if account_id in used_account_ids:
        return

    used_account_ids.add(account_id)

    cases.append({
        "name": name,
        "account_id": account_id,
        "expected": expected
    })


def get_account_health_test_cases():
    """
    Build diverse evaluation cases using only accounts
    available in the provided dataset.
    """

    accounts = load_accounts()

    used_account_ids = set()
    cases = []

    # Case 1: Explicit At Risk account
    at_risk_account = get_first_matching_account(
        accounts,
        lambda account: account.get("health_status") == "At Risk",
        used_account_ids
    )

    add_case(
        cases,
        used_account_ids,
        "At-risk account",
        at_risk_account,
        {
            "account_found": True,
            "has_executive_summary": True,
            "has_risks": True,
            "has_talking_points": True,
            "at_risk_signal_detected": True
        }
    )

    # Case 2: Inactive usage account
    inactive_account = get_first_matching_account(
        accounts,
        lambda account: account.get("usage_trend") == "Inactive",
        used_account_ids
    )

    add_case(
        cases,
        used_account_ids,
        "Inactive usage account",
        inactive_account,
        {
            "account_found": True,
            "has_executive_summary": True,
            "has_risks": True,
            "has_talking_points": True,
            "usage_decline_detected": True
        }
    )

    # Case 3: Highest open ticket volume
    remaining_accounts = get_remaining_accounts(
        accounts,
        used_account_ids
    )

    if remaining_accounts:
        high_open_tickets_account = max(
            remaining_accounts,
            key=lambda account: account.get("open_tickets", 0) or 0
        )

        add_case(
            cases,
            used_account_ids,
            "High open ticket volume",
            high_open_tickets_account,
            {
                "account_found": True,
                "has_executive_summary": True,
                "has_talking_points": True,
                "high_support_load_detected": True
            }
        )

    # Case 4: Highest ARR account
    remaining_accounts = get_remaining_accounts(
        accounts,
        used_account_ids
    )

    if remaining_accounts:
        high_arr_account = max(
            remaining_accounts,
            key=lambda account: account.get("arr_usd", 0) or 0
        )

        add_case(
            cases,
            used_account_ids,
            "High ARR account",
            high_arr_account,
            {
                "account_found": True,
                "has_executive_summary": True,
                "has_talking_points": True,
                "account_identity_correct": True
            }
        )

    # Case 5: Ticket-level dissatisfaction signal
    ticket_risk_account = get_first_matching_account(
        accounts,
        lambda account: (
            account.get("ticket_risk") is True
        ),
        used_account_ids
    )

    add_case(
        cases,
        used_account_ids,
        "Ticket-level dissatisfaction signal",
        ticket_risk_account,
        {
            "account_found": True,
            "has_executive_summary": True,
            "has_ticket_risk": True,
            "has_talking_points": True,
            "evidence_quote_present": True
        }
    )

    # Case 6: Adversarial missing account
    cases.append({
        "name": "Missing account ID adversarial case",
        "account_id": "ACC-DOES-NOT-EXIST",
        "expected": {
            "raises_clear_error": True
        }
    })

    return cases