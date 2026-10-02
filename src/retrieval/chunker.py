import re
from typing import List, Dict, Any


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> List[str]:
    """
    Split text into overlapping chunks, attempting to break cleanly
    on paragraphs or section headers where possible.
    """
    if not text or not text.strip():
        return []

    # Clean and normalize newlines
    clean_text = text.replace("\r\n", "\n").strip()
    text_length = len(clean_text)

    if text_length <= chunk_size:
        return [clean_text]

    chunks = []
    start = 0

    while start < text_length:
        end = start + chunk_size

        if end >= text_length:
            chunk = clean_text[start:text_length].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for natural breakpoint (double newline or single newline)
        breakpoint = clean_text.rfind("\n\n", start + chunk_size // 2, end)
        if breakpoint == -1:
            breakpoint = clean_text.rfind("\n", start + chunk_size // 2, end)
        if breakpoint == -1:
            breakpoint = clean_text.rfind(". ", start + chunk_size // 2, end)
            if breakpoint != -1:
                breakpoint += 1

        if breakpoint != -1 and breakpoint > start:
            chunk = clean_text[start:breakpoint].strip()
            next_start = max(start + 1, breakpoint - overlap)
        else:
            chunk = clean_text[start:end].strip()
            next_start = end - overlap

        if chunk:
            chunks.append(chunk)

        start = next_start

    return chunks


def create_chunks(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert KB documents into searchable chunks with metadata.
    """
    all_chunks: List[Dict[str, Any]] = []

    for document in documents:
        doc_name = document.get("document", "unknown.md")
        doc_path = document.get("path", doc_name)
        content = document.get("content", "")

        text_chunks = chunk_text(content)

        for index, chunk in enumerate(text_chunks):
            # Extract section heading if present in chunk
            heading_match = re.search(r"^(#{1,3}\s+[^\n]+)", chunk, re.MULTILINE)
            section_heading = heading_match.group(1).strip() if heading_match else ""

            all_chunks.append({
                "chunk_id": f"{doc_name}_chunk_{index}",
                "document": doc_name,
                "path": doc_path,
                "section": section_heading,
                "content": chunk
            })

    return all_chunks