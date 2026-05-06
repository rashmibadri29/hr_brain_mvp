from fastapi import APIRouter

from app.models.embeddings import RetrievalSearchRequest, RetrievalSearchResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()


@router.post("/retrieval/search", response_model=RetrievalSearchResponse)
def search_chunks(request: RetrievalSearchRequest) -> RetrievalSearchResponse:
    return RetrievalService().search(request)
