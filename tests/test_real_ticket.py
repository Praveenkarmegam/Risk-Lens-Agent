import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_tickets

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
# Load Dataset
# --------------------------------

tickets = load_tickets()


# --------------------------------
# Select a Ticket
# --------------------------------

ticket = tickets[0]


print("\nORIGINAL TICKET")
print("-" * 50)

print(
    "Ticket ID:",
    ticket["ticket_id"]
)

print(
    "Subject:",
    ticket["subject"]
)

print(
    "Body:",
    ticket["body"]
)


# --------------------------------
# Build KB Retriever
# --------------------------------

documents = load_knowledge_base()

chunks = create_chunks(
    documents
)

retriever = KnowledgeBaseRetriever(
    chunks
)


# --------------------------------
# AI TRIAGE
# --------------------------------

result = triage_ticket(
    subject=ticket["subject"],
    body=ticket["body"],
    retriever=retriever
)


# --------------------------------
# OUTPUT
# --------------------------------

print("\nAI TRIAGE RESULT")
print("-" * 50)

print(
    result.model_dump_json(
        indent=2
    )
)


# --------------------------------
# DATASET REFERENCE
# --------------------------------

print("\nDATASET LABELS")
print("-" * 50)

print(
    "Product:",
    ticket.get("product")
)

print(
    "Product Area:",
    ticket.get("product_area")
)

print(
    "Category:",
    ticket.get("category")
)

print(
    "Urgency:",
    ticket.get("urgency")
)