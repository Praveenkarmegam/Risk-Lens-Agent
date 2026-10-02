from pathlib import Path
from typing import List, Dict, Any
from src.config import KNOWLEDGE_BASE_DIR
from src.utils.sanitizer import safe_log_warning, safe_log_info


def load_knowledge_base(kb_dir: Path | None = None) -> List[Dict[str, Any]]:
    """
    Load all Markdown files from the knowledge base directory.

    Returns a list of dictionaries containing:
    - document: file name (e.g. 'authentication-sso.md')
    - path: relative posix path within KB (e.g. 'troubleshooting/authentication-sso.md')
    - content: full markdown text content
    """
    target_dir = Path(kb_dir) if kb_dir else KNOWLEDGE_BASE_DIR

    if not target_dir.exists():
        safe_log_warning(f"Knowledge base directory does not exist: {target_dir}")
        return []

    documents: List[Dict[str, Any]] = []
    markdown_files = sorted(list(target_dir.rglob("*.md")))

    for file_path in markdown_files:
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = file_path.relative_to(target_dir).as_posix()
            documents.append({
                "document": file_path.name,
                "path": relative_path,
                "content": content
            })
        except Exception as err:
            safe_log_warning(f"Failed to read KB document {file_path}: {err}")

    safe_log_info(f"Loaded {len(documents)} knowledge base documents from {target_dir}")
    return documents