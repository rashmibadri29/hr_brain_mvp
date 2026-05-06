import json
from pathlib import Path

from app.models.extraction import ExtractionRun, ExtractionRunDetail, ExtractedWorkflow


class ExtractionRepository:
    def __init__(self, store_path: Path):
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_store({"runs": [], "workflows": []})

    def list_runs(self) -> list[ExtractionRun]:
        data = self._read_store()
        return [ExtractionRun.model_validate(item) for item in data["runs"]]

    def get_run(self, run_id: str) -> ExtractionRunDetail | None:
        run = next((item for item in self.list_runs() if item.id == run_id), None)
        if run is None:
            return None
        return ExtractionRunDetail(**run.model_dump(), workflows=self.list_workflows(run_id=run_id))

    def add_run(self, run: ExtractionRun, workflows: list[ExtractedWorkflow]) -> ExtractionRunDetail:
        data = self._read_store()
        data["runs"].append(json.loads(run.model_dump_json()))
        data["workflows"] = [item for item in data["workflows"] if item["run_id"] != run.id]
        data["workflows"].extend(json.loads(workflow.model_dump_json()) for workflow in workflows)
        self._write_store(data)
        return ExtractionRunDetail(**run.model_dump(), workflows=workflows)

    def list_workflows(self, run_id: str | None = None) -> list[ExtractedWorkflow]:
        data = self._read_store()
        workflows = [ExtractedWorkflow.model_validate(item) for item in data["workflows"]]
        if run_id is not None:
            return [workflow for workflow in workflows if workflow.run_id == run_id]
        latest_by_name: dict[str, ExtractedWorkflow] = {}
        for workflow in sorted(workflows, key=lambda item: item.created_at):
            latest_by_name[workflow.name] = workflow
        return list(latest_by_name.values())

    def get_workflow(self, workflow_id: str) -> ExtractedWorkflow | None:
        return next((workflow for workflow in self.list_workflows() if workflow.id == workflow_id), None)

    def _read_store(self) -> dict[str, list[dict]]:
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _write_store(self, data: dict[str, list[dict]]) -> None:
        tmp_path = self.store_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self.store_path)
