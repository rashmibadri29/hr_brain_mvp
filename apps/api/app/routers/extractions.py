from fastapi import APIRouter, HTTPException, status

from app.models.extraction import ExtractionRun, ExtractionRunDetail, ExtractionRunRequest, ExtractionSummary, ExtractedWorkflow
from app.services.extraction_service import ExtractionNotFoundError, ExtractionService

router = APIRouter()


@router.get("/extractions/summary", response_model=ExtractionSummary)
def read_extraction_summary() -> ExtractionSummary:
    return ExtractionService().summary()


@router.post("/extractions/run", response_model=ExtractionRunDetail)
def run_extraction(request: ExtractionRunRequest | None = None) -> ExtractionRunDetail:
    return ExtractionService().run(request or ExtractionRunRequest())


@router.get("/extractions/runs", response_model=list[ExtractionRun])
def list_extraction_runs() -> list[ExtractionRun]:
    return ExtractionService().list_runs()


@router.get("/extractions/runs/{run_id}", response_model=ExtractionRunDetail)
def read_extraction_run(run_id: str) -> ExtractionRunDetail:
    try:
        return ExtractionService().get_run(run_id)
    except ExtractionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extraction run not found") from exc


@router.get("/extractions/workflows", response_model=list[ExtractedWorkflow])
def list_extracted_workflows() -> list[ExtractedWorkflow]:
    return ExtractionService().list_workflows()


@router.get("/extractions/workflows/{workflow_id}", response_model=ExtractedWorkflow)
def read_extracted_workflow(workflow_id: str) -> ExtractedWorkflow:
    try:
        return ExtractionService().get_workflow(workflow_id)
    except ExtractionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Extracted workflow not found") from exc
