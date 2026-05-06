from app.core.config import settings
from app.models.embeddings import RetrievedChunk, RetrievalSearchRequest, RetrievalSearchResponse
from app.services.embedding_repository import EmbeddingRepository
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_repository import IngestionRepository
from app.services.vectorizer import cosine_similarity, embed_text


class RetrievalService:
    def __init__(self) -> None:
        self.ingestion_repository = IngestionRepository(settings.ingestion_store_path)
        self.embedding_repository = EmbeddingRepository(settings.embedding_store_path)

    def search(self, request: RetrievalSearchRequest) -> RetrievalSearchResponse:
        if EmbeddingService().summary().missing_count > 0:
            EmbeddingService().rebuild()

        query_vector = embed_text(request.query)
        chunks_by_id = {chunk.id: chunk for chunk in self.ingestion_repository.list_chunks()}
        results: list[RetrievedChunk] = []

        for embedding in self.embedding_repository.list_embeddings():
            chunk = chunks_by_id.get(embedding.chunk_id)
            if chunk is None:
                continue
            if request.hr_domain and chunk.hr_domain.value != request.hr_domain:
                continue
            if request.source_document_id and chunk.source_document_id != request.source_document_id:
                continue
            similarity = cosine_similarity(query_vector, embedding.vector)
            results.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    source_document_id=chunk.source_document_id,
                    source_title=chunk.source_title,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    hr_domain=chunk.hr_domain.value,
                    risk_level=chunk.risk_level,
                    sensitivity_label=chunk.sensitivity_label.value,
                    citation_label=chunk.citation_label,
                    similarity=round(similarity, 6),
                )
            )

        results.sort(key=lambda item: item.similarity, reverse=True)
        return RetrievalSearchResponse(query=request.query, results=results[: request.top_k])
