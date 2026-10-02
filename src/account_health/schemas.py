from typing import List, Literal

from pydantic import BaseModel


RiskSeverity = Literal[
    "High",
    "Medium",
    "Low"
]


class FlaggedIssue(BaseModel):

    risk_type: str

    severity: RiskSeverity

    source: Literal[
        "account",
        "ticket"
    ]

    reason: str

    ticket_id: str | None = None

    evidence_quote: str | None = None


class AccountHealthNarrative(BaseModel):

    executive_summary: str

    recommended_talking_points: List[str]


class AccountHealthBrief(BaseModel):

    account_id: str

    company: str

    executive_summary: str

    open_risks_and_flagged_issues: List[
        FlaggedIssue
    ]

    recommended_talking_points: List[str]