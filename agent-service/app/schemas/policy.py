from pydantic import BaseModel, Field


class PolicyChunk(BaseModel):
    chunk_id: str
    document_name: str
    section_title: str
    text: str
    policy_code: str | None = None


class PolicyReference(BaseModel):
    policy_code: str | None = None
    document_name: str
    section_title: str
    content: str
    score: float = Field(ge=0)
