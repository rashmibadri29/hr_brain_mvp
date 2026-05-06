import json
from pathlib import Path

from app.models.embeddings import ChunkEmbedding


class EmbeddingRepository:
    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_store({"embeddings": []})

    def list_embeddings(self) -> list[ChunkEmbedding]:
        data = self._read_store()
        return [ChunkEmbedding.model_validate(item) for item in data["embeddings"]]

    def replace_embeddings(self, embeddings: list[ChunkEmbedding]) -> list[ChunkEmbedding]:
        self._write_store({"embeddings": [json.loads(item.model_dump_json()) for item in embeddings]})
        return embeddings

    def _read_store(self) -> dict[str, list[dict]]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, data: dict[str, list[dict]]) -> None:
        tmp_path = self.store_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self.store_path)
