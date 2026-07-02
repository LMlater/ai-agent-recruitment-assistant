import re
from pathlib import Path

from app.core.config import settings
from app.schemas.policy import PolicyChunk


POLICY_CODE_RE = re.compile(r"\b[A-Z]-\d{3}\b")


class PolicyDocumentLoader:
    def __init__(self, knowledge_base_dir: Path | None = None) -> None:
        self.knowledge_base_dir = knowledge_base_dir or settings.knowledge_base_dir

    def load_chunks(self) -> list[PolicyChunk]:
        if not self.knowledge_base_dir.exists():
            return []

        chunks: list[PolicyChunk] = []
        for path in sorted(self.knowledge_base_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            chunks.extend(self._split_document(path.name, content))
        return chunks

    def _split_document(self, document_name: str, content: str) -> list[PolicyChunk]:
        sections: list[tuple[str, list[str]]] = []
        current_title: str | None = None
        current_lines: list[str] = []

        for line in content.splitlines():
            if line.startswith("## "):
                if current_title is not None:
                    sections.append((current_title, current_lines))
                current_title = line[3:].strip()
                current_lines = []
                continue
            if current_title is not None:
                current_lines.append(line)

        if current_title is not None:
            sections.append((current_title, current_lines))
        elif content:
            title = self._first_heading_or_name(document_name, content)
            sections.append((title, content.splitlines()))

        chunks: list[PolicyChunk] = []
        for index, (section_title, lines) in enumerate(sections, start=1):
            body = "\n".join(line for line in lines).strip()
            text = f"{section_title}\n\n{body}".strip()
            if not text:
                continue
            policy_code = self._extract_policy_code(section_title, text)
            chunk_id = f"{document_name}::{policy_code or self._slugify(section_title, index)}"
            chunks.append(
                PolicyChunk(
                    chunk_id=chunk_id,
                    document_name=document_name,
                    section_title=section_title,
                    text=text,
                    policy_code=policy_code,
                )
            )
        return chunks

    def _extract_policy_code(self, section_title: str, text: str) -> str | None:
        match = POLICY_CODE_RE.search(f"{section_title}\n{text}")
        return match.group(0) if match else None

    def _first_heading_or_name(self, document_name: str, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return document_name

    def _slugify(self, value: str, index: int) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or f"section-{index:03d}"
