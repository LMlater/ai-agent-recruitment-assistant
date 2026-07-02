from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.policy import PolicyChunk, PolicyReference
from app.services.policy_document_loader import PolicyDocumentLoader


class PolicyRetrievalService:
    def __init__(self, knowledge_base_dir: Path | None = None, min_score: float = 0.01) -> None:
        self.knowledge_base_dir = knowledge_base_dir
        self.min_score = min_score
        self.loader = PolicyDocumentLoader(knowledge_base_dir)
        self.chunks = self.loader.load_chunks()
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._build_index()

    def search(self, query: str, top_k: int = 5) -> list[PolicyReference]:
        if not query.strip() or not self.chunks or self._vectorizer is None or self._matrix is None:
            return []

        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix).ravel()
        ranked_indexes = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)

        references: list[PolicyReference] = []
        for index in ranked_indexes:
            score = float(scores[index])
            if score <= self.min_score:
                continue
            references.append(self._to_reference(self.chunks[index], score))
            if len(references) >= top_k:
                break
        return references

    def _build_index(self) -> None:
        if not self.chunks:
            return
        self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), lowercase=True)
        self._matrix = self._vectorizer.fit_transform([chunk.text for chunk in self.chunks])

    def _to_reference(self, chunk: PolicyChunk, score: float) -> PolicyReference:
        return PolicyReference(
            policy_code=chunk.policy_code,
            document_name=chunk.document_name,
            section_title=chunk.section_title,
            content=chunk.text,
            score=round(score, 4),
        )
