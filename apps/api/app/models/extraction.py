from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ExtractionRunStatus(StrEnum):
    completed = "completed"
    failed = "failed"


class ExtractionCitation(BaseModel):
    chunk_id: str
    source_document_id: str
    source_title: str
    citation_label: str
    excerpt: str
    similarity: float | None = None


class ExtractedRequiredInput(BaseModel):
    name: str
    description: str
    sensitive: bool = False
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedWorkflowStep(BaseModel):
    order: int
    title: str
    instruction: str
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedPolicyRule(BaseModel):
    title: str
    rule: str
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedEligibilityRule(BaseModel):
    title: str
    rule: str
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedApprovalRule(BaseModel):
    title: str
    condition: str
    approver_role: str
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedEscalationRule(BaseModel):
    title: str
    trigger: str
    destination: str
    citations: list[ExtractionCitation] = Field(default_factory=list)


class ExtractedWorkflow(BaseModel):
    id: str
    run_id: str
    name: str
    description: str
    hr_domain: str
    risk_level: str
    confidence: float = Field(ge=0, le=1)
    required_inputs: list[ExtractedRequiredInput] = Field(default_factory=list)
    steps: list[ExtractedWorkflowStep] = Field(default_factory=list)
    policy_rules: list[ExtractedPolicyRule] = Field(default_factory=list)
    eligibility_rules: list[ExtractedEligibilityRule] = Field(default_factory=list)
    approval_rules: list[ExtractedApprovalRule] = Field(default_factory=list)
    escalation_rules: list[ExtractedEscalationRule] = Field(default_factory=list)
    citations: list[ExtractionCitation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExtractionRun(BaseModel):
    id: str
    status: ExtractionRunStatus
    workflow_count: int
    chunk_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    error_message: str | None = None


class ExtractionRunDetail(ExtractionRun):
    workflows: list[ExtractedWorkflow] = Field(default_factory=list)


class ExtractionSummary(BaseModel):
    run_count: int
    workflow_count: int
    latest_run_id: str | None = None
    latest_run_at: datetime | None = None


class ExtractionRunRequest(BaseModel):
    rebuild_embeddings: bool = True
