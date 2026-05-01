from enum import StrEnum

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class WorkflowStatus(StrEnum):
    defined = "defined"
    draft = "draft"
    needs_review = "needs_review"
    approved = "approved"
    published = "published"
    deprecated = "deprecated"


class SourceCitation(BaseModel):
    source_id: str
    source_title: str
    chunk_id: str | None = None
    excerpt: str | None = None


class RequiredInput(BaseModel):
    name: str
    description: str
    sensitive: bool = False


class WorkflowStep(BaseModel):
    order: int = Field(ge=1)
    title: str
    instruction: str
    owner: str | None = None


class PolicyRule(BaseModel):
    title: str
    rule: str
    applies_to: list[str] = Field(default_factory=list)
    citations: list[SourceCitation] = Field(default_factory=list)


class ApprovalRule(BaseModel):
    title: str
    condition: str
    approver_role: str


class EscalationRule(BaseModel):
    title: str
    trigger: str
    destination: str
    required: bool = True


class HRWorkflow(BaseModel):
    id: str
    name: str
    description: str
    risk_level: RiskLevel
    status: WorkflowStatus = WorkflowStatus.defined
    allowed_ai_behaviors: list[str] = Field(default_factory=list)
    disallowed_ai_behaviors: list[str] = Field(default_factory=list)
    required_inputs: list[RequiredInput] = Field(default_factory=list)
    steps: list[WorkflowStep] = Field(default_factory=list)
    policy_rules: list[PolicyRule] = Field(default_factory=list)
    approval_rules: list[ApprovalRule] = Field(default_factory=list)
    escalation_rules: list[EscalationRule] = Field(default_factory=list)


class SafetyPolicy(BaseModel):
    allowed_ai_behaviors: list[str]
    disallowed_ai_behaviors: list[str]
    mandatory_escalation_triggers: list[str]
    publication_requirements: list[str]


class SkillFile(BaseModel):
    workflow_id: str
    title: str
    version: str
    markdown: str
    approved: bool = False


class MvpScope(BaseModel):
    product_name: str
    phase: str
    workflows: list[HRWorkflow]
    safety_policy: SafetyPolicy
    success_metrics: list[str]

