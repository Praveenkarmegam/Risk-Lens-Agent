import sys
from pathlib import Path
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


documents = load_knowledge_base()

chunks = create_chunks(
    documents
)

retriever = KnowledgeBaseRetriever(
    chunks
)


subject = (
    "Platform unavailable for all users"
)


body = """
All users in our organisation are unable
to access the platform.

The service appears completely unavailable
and our production workflows have stopped.
"""


result = triage_ticket(
    subject=subject,
    body=body,
    retriever=retriever
)


print(
    result.model_dump_json(
        indent=2
    )
)