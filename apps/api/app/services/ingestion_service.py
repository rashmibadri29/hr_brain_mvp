import re
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.models.ingestion import (
    DocumentChunk,
    HRDomain,
    IngestionSummary,
    ProcessingStatus,
    SensitivityLabel,
    SourceDocument,
    SourceDocumentDetail,
    SourceType,
)
from app.services.ingestion_chunker import chunk_text
from app.services.ingestion_parser import SUPPORTED_EXTENSIONS, parse_file
from app.services.ingestion_repository import IngestionRepository, utcnow


class SourceNotFoundError(LookupError):
    pass


class IngestionService:
    def __init__(self) -> None:
        self.data_dir = settings.data_dir_path
        self.upload_dir = settings.upload_dir_path
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.repository = IngestionRepository(settings.ingestion_store_path)

    def summary(self) -> IngestionSummary:
        sources = self.repository.list_sources()
        chunks = self.repository.list_chunks()
        return IngestionSummary(
            source_count=len(sources),
            chunk_count=len(chunks),
            parsed_count=sum(1 for source in sources if source.processing_status == ProcessingStatus.parsed),
            failed_count=sum(1 for source in sources if source.processing_status == ProcessingStatus.failed),
            supported_file_types=SUPPORTED_EXTENSIONS,
        )

    def list_sources(self) -> list[SourceDocument]:
        return self.repository.list_sources()

    def get_source_detail(self, source_id: str) -> SourceDocumentDetail:
        source = self.repository.get_source(source_id)
        if source is None:
            raise SourceNotFoundError(source_id)
        return SourceDocumentDetail(**source.model_dump(), chunks=self.repository.list_chunks(source_id))

    def list_chunks(self, source_id: str) -> list[DocumentChunk]:
        if self.repository.get_source(source_id) is None:
            raise SourceNotFoundError(source_id)
        return self.repository.list_chunks(source_id)

    async def ingest_upload(
        self,
        *,
        file: UploadFile,
        title: str | None,
        source_type: SourceType,
        uploaded_by: str | None,
    ) -> SourceDocumentDetail:
        source_id = f"src_{uuid4().hex[:12]}"
        original_filename = file.filename or "uploaded-source"
        safe_filename = _safe_filename(original_filename)
        storage_path = self.upload_dir / f"{source_id}_{safe_filename}"

        with storage_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        source = SourceDocument(
            id=source_id,
            title=title or Path(original_filename).stem.replace("_", " ").replace("-", " ").title(),
            original_filename=original_filename,
            source_type=source_type,
            content_type=file.content_type,
            storage_path=str(storage_path.relative_to(self.data_dir)),
            processing_status=ProcessingStatus.parsing,
            uploaded_by=uploaded_by,
        )
        self.repository.upsert_source(source)

        try:
            parsed_text = parse_file(storage_path)
            chunks = chunk_text(
                text=parsed_text,
                source_document_id=source.id,
                source_title=source.title,
            )
            self.repository.replace_chunks(source.id, chunks)
            source.processing_status = ProcessingStatus.parsed
            source.processed_at = utcnow()
            source.error_message = None
            source.chunk_count = len(chunks)
            source.detected_domains = _unique_domains(chunks)
            source.sensitivity_labels = _unique_sensitivity_labels(chunks)
        except Exception as exc:  # Surface parser errors to the review UI while preserving the upload record.
            source.processing_status = ProcessingStatus.failed
            source.processed_at = utcnow()
            source.error_message = str(exc)
            source.chunk_count = 0
            self.repository.replace_chunks(source.id, [])

        self.repository.upsert_source(source)
        return self.get_source_detail(source.id)


def _safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
    return cleaned or "uploaded-source"


def _unique_domains(chunks: list[DocumentChunk]) -> list[HRDomain]:
    seen: list[HRDomain] = []
    for chunk in chunks:
        if chunk.hr_domain not in seen:
            seen.append(chunk.hr_domain)
    return seen


def _unique_sensitivity_labels(chunks: list[DocumentChunk]) -> list[SensitivityLabel]:
    seen: list[SensitivityLabel] = []
    for chunk in chunks:
        if chunk.sensitivity_label != SensitivityLabel.none and chunk.sensitivity_label not in seen:
            seen.append(chunk.sensitivity_label)
    return seen
