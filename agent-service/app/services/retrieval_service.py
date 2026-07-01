from pathlib import Path
from typing import Iterable

from app.core.config import settings


class RetrievalService:
    """Keyword retrieval placeholder for later Chroma or FAISS integration."""

    def __init__(self, knowledge_base_dir: Path | None = None) -> None:
        self.knowledge_base_dir = knowledge_base_dir or settings.knowledge_base_dir

    def search(self, terms: Iterable[str], limit: int = 6) -> list[str]:
        normalized_terms = [term.lower() for term in terms if term]
        matches: list[str] = []
        for path in sorted(self.knowledge_base_dir.glob("*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                lower = stripped.lower()
                if any(term in lower for term in normalized_terms):
                    matches.append(f"{path.name}: {stripped}")
                if len(matches) >= limit:
                    return matches
        return matches
