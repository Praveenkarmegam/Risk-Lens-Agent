from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


IssueCategory = Literal[
    "Bug",
    "Incident",
    "Feature Request",
    "Integration",
    "Performance",
    "Authentication",
    "Billing",
    "How-to",
    "Other"
]

Priority = Literal[
    "P1",
    "P2",
    "P3",
    "P4"
]

ConfidenceLevel = Literal[
    "High",
    "Medium",
    "Low"
]


class KnowledgeBaseReference(BaseModel):
    document: str = Field(..., description="Name of the referenced KB markdown document")
    path: str = Field(..., description="Relative path of the document within the knowledge base")
    relevance_reason: str = Field(..., description="Specific explanation of why this document applies to the ticket")


class TicketTriageResult(BaseModel):
    product_area: str = Field(
        default="General",
        description="Functional product area or module (e.g., Authentication, Data Ingestion, Dashboard)"
    )
    issue_category: IssueCategory = Field(
        default="Other",
        description="Classified ticket intent category"
    )
    priority: Priority = Field(
        default="P3",
        description="Assigned severity level (P1 critical outage to P4 minor query)"
    )
    confidence: ConfidenceLevel = Field(
        default="Medium",
        description="Confidence bucket (High, Medium, Low)"
    )
    confidence_score: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Calculated confidence score between 0.0 and 1.0"
    )
    needs_clarification: bool = Field(
        default=False,
        description="True if ticket information is ambiguous, contradictory, or severely incomplete"
    )
    clarifying_questions: List[str] = Field(
        default_factory=list,
        description="1-3 targeted questions to ask user if clarification is needed"
    )
    retrieved_facts: List[str] = Field(
        default_factory=list,
        description="Direct verifiable facts extracted from retrieved KB or ticket body, separated from reasoning"
    )
    model_reasoning: str = Field(
        default="",
        description="Model-generated analytical reasoning leading to classification"
    )
    reasoning: str = Field(
        default="",
        description="Concise summary of rationale (maintained for backward compatibility)"
    )
    known_issue: bool = Field(
        default=False,
        description="True only if retrieved KB explicitly documents this as a known bug, limitation, or outage"
    )
    knowledge_base_references: List[KnowledgeBaseReference] = Field(
        default_factory=list,
        description="List of relevant KB documents cited with specific reasons"
    )
    recommended_team: str = Field(
        default="Technical Support",
        description="Target routing queue (e.g. Identity & Security, Platform Core, Billing Operations)"
    )
    draft_first_response: str = Field(
        default="",
        description="Customer-facing acknowledgment adhering to strict communication guidelines"
    )
    audit_notes: str = Field(
        default="",
        description="Audit trail notes detailing applied guardrails, retrieval stats, and review flags"
    )
    flagged_for_human_review: bool = Field(
        default=False,
        description="True if low confidence, ambiguity, or guardrail overrides require human intervention"
    )

    @field_validator("reasoning", mode="before")
    @classmethod
    def populate_reasoning(cls, v, info):
        """Ensure reasoning is non-empty if model_reasoning was provided."""
        if (not v or not str(v).strip()) and info.data.get("model_reasoning"):
            return str(info.data.get("model_reasoning"))
        return v or "Ticket triaged according to standard classification guidelines."

    @field_validator("model_reasoning", mode="before")
    @classmethod
    def populate_model_reasoning(cls, v, info):
        """Ensure model_reasoning is non-empty if reasoning was provided."""
        if (not v or not str(v).strip()) and info.data.get("reasoning"):
            return str(info.data.get("reasoning"))
        return v or ""