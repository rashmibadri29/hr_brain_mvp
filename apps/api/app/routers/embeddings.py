from fastapi import APIRouter

from app.models.embeddings import EmbeddingRebuildResult, EmbeddingSummary
from app.services.embedding_service import EmbeddingService

router = APIRouter()


@router.get("/embeddings/summary", response_model=EmbeddingSummary)
def read_embedding_summary() -> EmbeddingSummary:
    return EmbeddingService().summary()


@router.post("/embeddings/rebuild", response_model=EmbeddingRebuildResult)
def rebuild_embeddings() -> EmbeddingRebuildResult:
    return EmbeddingService().rebuild()
