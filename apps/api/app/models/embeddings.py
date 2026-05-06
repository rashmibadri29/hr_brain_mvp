from datetime import datetime

from pydantic import BaseModel, Field


class ChunkEmbedding(BaseModel):
    chunk_id: str
    source_document_id: str
    embedding_model: str
    vector: list[float]
    embedded_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddingSummary(BaseModel):
    embedding_count: int
    chunk_count: int
    missing_count: int
    embedding_model: str
    dimensions: int


class EmbeddingRebuildResult(EmbeddingSummary):
    rebuilt_count: int


class RetrievalSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    hr_domain: str | None = None
    source_document_id: str | None = None


class RetrievedChunk(BaseModel):
    chunk_id: str
    source_document_id: str
    source_title: str
    chunk_index: int
    content: str
    hr_domain: str
    risk_level: str
    sensitivity_label: str
    citation_label: str
    similarity: float


class RetrievalSearchResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]
