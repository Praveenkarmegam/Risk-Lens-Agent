TRIAGE_TEST_CASES = [

    {
        "name": "Feature request with workaround",

        "subject": (
            "Request: bulk archive operations"
        ),

        "body": """
        We currently have to archive records one
        at a time.

        We need the ability to select multiple
        records and archive them in bulk.

        Current workaround is manually processing
        each record.
        """,

        "expected_category": (
            "Feature Request"
        ),

        "allowed_priorities": [
            "P3",
            "P4"
        ]
    },


    {
        "name": "SSO authentication failure",

        "subject": (
            "Multiple users cannot log in via SSO"
        ),

        "body": """
        Multiple employees are receiving SSO
        authentication errors.

        They are unable to access the application.
        """,

        "expected_category": (
            "Authentication"
        ),

        "allowed_priorities": [
            "P2",
            "P3"
        ]
    },


    {
        "name": "General how-to question",

        "subject": (
            "How do I update notification settings?"
        ),

        "body": """
        I would like to change the notification
        settings for my account.

        Please explain where this can be configured.
        """,

        "expected_category": (
            "How-to"
        ),

        "allowed_priorities": [
            "P4"
        ]
    },


    {
        "name": "Potential production outage",

        "subject": (
            "Platform unavailable for all users"
        ),

        "body": """
        All users in our organisation are unable
        to access the platform.

        The service appears completely unavailable
        and our production workflows have stopped.
        """,

        "expected_category": (
            "Incident"
        ),

        "allowed_priorities": [
            "P1"
        ]
    },


    {
        "name": "Performance issue",

        "subject": (
            "Analytics dashboard is extremely slow"
        ),

        "body": """
        Dashboard pages are taking more than
        30 seconds to load.

        The issue is affecting our team's ability
        to complete daily reporting work.
        """,

        "expected_category": (
            "Performance"
        ),

        "allowed_priorities": [
            "P2",
            "P3"
        ]
    },


    {
        "name": "Incomplete ticket",

        "subject": "Not working",

        "body": """
        Something is not working correctly.
        Please fix this.
        """,

        "expected_category": None,

        "allowed_priorities": [
            "P3",
            "P4"
        ],
        "expects_clarification": True
    }
]