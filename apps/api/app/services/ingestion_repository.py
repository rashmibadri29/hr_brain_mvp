import json
from datetime import datetime
from pathlib import Path

from app.models.ingestion import DocumentChunk, SourceDocument


class IngestionRepository:
    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_store({"sources": [], "chunks": []})

    def list_sources(self) -> list[SourceDocument]:
        data = self._read_store()
        return [SourceDocument.model_validate(item) for item in data["sources"]]

    def get_source(self, source_id: str) -> SourceDocument | None:
        return next((source for source in self.list_sources() if source.id == source_id), None)

    def upsert_source(self, source: SourceDocument) -> SourceDocument:
        data = self._read_store()
        sources = [item for item in data["sources"] if item["id"] != source.id]
        sources.append(_jsonable(source))
        data["sources"] = sorted(sources, key=lambda item: item["uploaded_at"], reverse=True)
        self._write_store(data)
        return source

    def replace_chunks(self, source_id: str, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        data = self._read_store()
        data["chunks"] = [item for item in data["chunks"] if item["source_document_id"] != source_id]
        data["chunks"].extend(_jsonable(chunk) for chunk in chunks)
        self._write_store(data)
        return chunks

    def list_chunks(self, source_id: str | None = None) -> list[DocumentChunk]:
        data = self._read_store()
        chunks = [DocumentChunk.model_validate(item) for item in data["chunks"]]
        if source_id is not None:
            return [chunk for chunk in chunks if chunk.source_document_id == source_id]
        return chunks

    def _read_store(self) -> dict[str, list[dict]]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, data: dict[str, list[dict]]) -> None:
        tmp_path = self.store_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self.store_path)


def _jsonable(model: SourceDocument | DocumentChunk) -> dict:
    return json.loads(model.model_dump_json())


def utcnow() -> datetime:
    return datetime.utcnow()
