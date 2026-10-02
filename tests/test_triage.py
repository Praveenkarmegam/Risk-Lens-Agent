import sys
from pathlib import Path

# Add project root to sys.path for standalone script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retrieval.kb_loader import (
    load_knowledge_base
)

from src.retrieval.chunker import (
    create_chunks
)

from src.retrieval.retriever import (
    KnowledgeBaseRetriever
)

from src.triage.service import (
    triage_ticket
)


# --------------------------------
# Build the KB retriever
# --------------------------------

documents = load_knowledge_base()

chunks = create_chunks(
    documents
)

retriever = KnowledgeBaseRetriever(
    chunks
)


# --------------------------------
# Test Ticket
# --------------------------------

subject = (
    "Users cannot log in through SSO"
)

body = """
Multiple employees are unable to log into
the platform through our SSO provider.

They are receiving authentication errors.

This is preventing several users from
accessing the application.
"""


# --------------------------------
# Run Triage
# --------------------------------

result = triage_ticket(
    subject=subject,
    body=body,
    retriever=retriever
)


# --------------------------------
# Print Result
# --------------------------------

print(
    result.model_dump_json(
        indent=2
    )
)