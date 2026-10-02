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


# Load KB documents
documents = load_knowledge_base()

print(
    "KB Documents:",
    len(documents)
)


# Create chunks
chunks = create_chunks(
    documents
)

print(
    "Total Chunks:",
    len(chunks)
)


# Create retriever
retriever = (
    KnowledgeBaseRetriever(
        chunks
    )
)


# Test query
query = (
    "Users cannot log in using "
    "single sign-on and are receiving "
    "authentication errors"
)


results = retriever.search(
    query=query,
    top_k=3
)


print("\nQUERY:")
print(query)


print("\nTOP RESULTS:")

for result in results:

    print(
        "\n-------------------------"
    )

    print(
        "Document:",
        result["document"]
    )

    print(
        "Path:",
        result["path"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "\nContent:"
    )

    print(
        result["content"][:500]
    )