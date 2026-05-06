from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.ingestion import DocumentChunk, IngestionSummary, SourceDocument, SourceDocumentDetail, SourceType
from app.services.ingestion_service import IngestionService, SourceNotFoundError

router = APIRouter()


def get_ingestion_service() -> IngestionService:
    return IngestionService()


@router.get("/sources/summary", response_model=IngestionSummary)
def read_ingestion_summary() -> IngestionSummary:
    return get_ingestion_service().summary()


@router.get("/sources", response_model=list[SourceDocument])
def list_sources() -> list[SourceDocument]:
    return get_ingestion_service().list_sources()


@router.post("/sources", response_model=SourceDocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_source(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    source_type: SourceType = Form(default=SourceType.other),
    uploaded_by: str | None = Form(default=None),
) -> SourceDocumentDetail:
    return await get_ingestion_service().ingest_upload(
        file=file,
        title=title,
        source_type=source_type,
        uploaded_by=uploaded_by,
    )


@router.get("/sources/{source_id}", response_model=SourceDocumentDetail)
def read_source(source_id: str) -> SourceDocumentDetail:
    try:
        return get_ingestion_service().get_source_detail(source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from exc


@router.get("/sources/{source_id}/chunks", response_model=list[DocumentChunk])
def read_source_chunks(source_id: str) -> list[DocumentChunk]:
    try:
        return get_ingestion_service().list_chunks(source_id)
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from exc
