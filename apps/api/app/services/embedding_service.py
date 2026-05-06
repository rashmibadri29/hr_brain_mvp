from app.core.config import settings
from app.models.embeddings import ChunkEmbedding, EmbeddingRebuildResult, EmbeddingSummary
from app.services.embedding_repository import EmbeddingRepository
from app.services.ingestion_repository import IngestionRepository
from app.services.vectorizer import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, embed_text


class EmbeddingService:
    def __init__(self) -> None:
        self.ingestion_repository = IngestionRepository(settings.ingestion_store_path)
        self.embedding_repository = EmbeddingRepository(settings.embedding_store_path)

    def summary(self) -> EmbeddingSummary:
        chunks = self.ingestion_repository.list_chunks()
        embeddings = self.embedding_repository.list_embeddings()
        embedded_chunk_ids = {embedding.chunk_id for embedding in embeddings}
        return EmbeddingSummary(
            embedding_count=len(embeddings),
            chunk_count=len(chunks),
            missing_count=sum(1 for chunk in chunks if chunk.id not in embedded_chunk_ids),
            embedding_model=EMBEDDING_MODEL,
            dimensions=EMBEDDING_DIMENSIONS,
        )

    def rebuild(self) -> EmbeddingRebuildResult:
        chunks = self.ingestion_repository.list_chunks()
        embeddings = [
            ChunkEmbedding(
                chunk_id=chunk.id,
                source_document_id=chunk.source_document_id,
                embedding_model=EMBEDDING_MODEL,
                vector=embed_text(chunk.content),
            )
            for chunk in chunks
        ]
        self.embedding_repository.replace_embeddings(embeddings)
        summary = self.summary()
        return EmbeddingRebuildResult(**summary.model_dump(), rebuilt_count=len(embeddings))
