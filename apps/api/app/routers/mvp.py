from fastapi import APIRouter

from app.models.hr_brain import MvpScope, SafetyPolicy
from app.services.mvp_scope import get_mvp_scope

router = APIRouter()


@router.get("/scope", response_model=MvpScope)
def read_scope() -> MvpScope:
    return get_mvp_scope()


@router.get("/workflows")
def read_workflows() -> list[dict[str, str]]:
    scope = get_mvp_scope()
    return [
        {
            "id": workflow.id,
            "name": workflow.name,
            "risk_level": workflow.risk_level.value,
            "status": workflow.status.value,
            "description": workflow.description,
        }
        for workflow in scope.workflows
    ]


@router.get("/safety-policy", response_model=SafetyPolicy)
def read_safety_policy() -> SafetyPolicy:
    return get_mvp_scope().safety_policy

