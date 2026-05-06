from uuid import uuid4

from app.core.config import settings
from app.models.embeddings import RetrievalSearchRequest, RetrievedChunk
from app.models.extraction import (
    ExtractionCitation,
    ExtractionRun,
    ExtractionRunDetail,
    ExtractionRunRequest,
    ExtractionRunStatus,
    ExtractionSummary,
    ExtractedApprovalRule,
    ExtractedEligibilityRule,
    ExtractedEscalationRule,
    ExtractedPolicyRule,
    ExtractedRequiredInput,
    ExtractedWorkflow,
    ExtractedWorkflowStep,
)
from app.services.embedding_service import EmbeddingService
from app.services.extraction_repository import ExtractionRepository
from app.services.ingestion_repository import IngestionRepository
from app.services.retrieval_service import RetrievalService


WORKFLOW_SPECS = [
    {
        "slug": "new-hire-onboarding",
        "name": "New Hire Onboarding",
        "domain": "onboarding",
        "query": "new hire onboarding first day manager role start date employment type work location laptop account setup",
        "description": "Draft onboarding checklist and routing rules for new employees.",
        "risk_level": "medium",
        "required_inputs": [
            ("employee_name", "New hire full name", True),
            ("start_date", "Expected first day", False),
            ("role", "Job title or role", False),
            ("manager", "Hiring manager", False),
            ("location", "Work location or jurisdiction", False),
            ("employment_type", "Full-time, part-time, contractor, or intern", False),
        ],
        "steps": [
            ("Collect onboarding context", "Gather employee name, role, start date, manager, location, and employment type."),
            ("Prepare preboarding tasks", "Identify HR paperwork, payroll setup, benefits eligibility, IT equipment, and account setup tasks."),
            ("Escalate missing details", "Route unclear employment type, location, or manager assignment to HR operations."),
        ],
    },
    {
        "slug": "pto-leave-guidance",
        "name": "PTO And Leave Guidance",
        "domain": "pto_leave",
        "query": "PTO vacation sick leave parental leave FMLA medical leave disability accommodation policy exception approval",
        "description": "Draft guidance for PTO and leave questions with required escalation boundaries.",
        "risk_level": "high",
        "required_inputs": [
            ("employee_location", "Employee work location or jurisdiction", False),
            ("employment_type", "Employee classification", False),
            ("leave_type", "PTO, sick leave, parental leave, medical leave, or other leave category", False),
        ],
        "steps": [
            ("Identify applicable policy", "Determine employee location, employment type, and leave category."),
            ("Answer from approved sources", "Summarize the applicable policy and cite the source chunks."),
            ("Escalate protected or exception cases", "Escalate medical, legal, protected leave, accommodation, or exception requests to HR."),
        ],
    },
    {
        "slug": "payroll-issue-intake",
        "name": "Payroll Issue Intake",
        "domain": "payroll",
        "query": "payroll paycheck pay period deduction direct deposit tax incorrect amount compensation dispute",
        "description": "Draft intake workflow for payroll questions without changing payroll records.",
        "risk_level": "medium",
        "required_inputs": [
            ("pay_period", "Affected pay period", False),
            ("issue_type", "Missing pay, incorrect amount, deduction issue, tax issue, direct deposit issue, or other", False),
            ("employee_summary", "Employee description of the issue", True),
        ],
        "steps": [
            ("Collect issue details", "Gather pay period, issue type, and employee summary."),
            ("Classify urgency", "Identify whether the issue involves missing pay, deductions, direct deposit, tax, or compensation dispute."),
            ("Route to payroll", "Send a structured intake summary to the payroll owner."),
        ],
    },
    {
        "slug": "benefits-eligibility-guidance",
        "name": "Benefits Eligibility Guidance",
        "domain": "benefits",
        "query": "benefits eligibility enrollment health dental vision 401k qualifying life event medical accommodation",
        "description": "Draft benefits eligibility and enrollment guidance from approved source chunks.",
        "risk_level": "medium",
        "required_inputs": [
            ("employment_type", "Employee classification", False),
            ("start_date", "Employee start date", False),
            ("benefit_type", "Medical, dental, vision, retirement, or other benefit", False),
        ],
        "steps": [
            ("Identify eligibility context", "Gather employment type, start date, and requested benefit type."),
            ("Explain enrollment rule", "Summarize eligibility and enrollment window from cited sources."),
            ("Escalate exceptions", "Route benefits exceptions, medical accommodation, or unclear eligibility cases to HR benefits."),
        ],
    },
]


class ExtractionNotFoundError(LookupError):
    pass


class ExtractionService:
    def __init__(self) -> None:
        self.repository = ExtractionRepository(settings.extraction_store_path)
        self.ingestion_repository = IngestionRepository(settings.ingestion_store_path)
        self.retrieval_service = RetrievalService()
        self.embedding_service = EmbeddingService()

    def summary(self) -> ExtractionSummary:
        runs = self.repository.list_runs()
        workflows = self.repository.list_workflows()
        latest = max(runs, key=lambda item: item.created_at) if runs else None
        return ExtractionSummary(
            run_count=len(runs),
            workflow_count=len(workflows),
            latest_run_id=latest.id if latest else None,
            latest_run_at=latest.created_at if latest else None,
        )

    def run(self, request: ExtractionRunRequest) -> ExtractionRunDetail:
        if request.rebuild_embeddings:
            self.embedding_service.rebuild()
        elif self.embedding_service.summary().missing_count > 0:
            self.embedding_service.rebuild()

        run_id = f"run_{uuid4().hex[:12]}"
        workflows = [self._extract_workflow(run_id, spec) for spec in WORKFLOW_SPECS]
        workflows = [workflow for workflow in workflows if workflow.citations]
        run = ExtractionRun(
            id=run_id,
            status=ExtractionRunStatus.completed,
            workflow_count=len(workflows),
            chunk_count=len(self.ingestion_repository.list_chunks()),
        )
        return self.repository.add_run(run, workflows)

    def list_runs(self) -> list[ExtractionRun]:
        return self.repository.list_runs()

    def get_run(self, run_id: str) -> ExtractionRunDetail:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ExtractionNotFoundError(run_id)
        return run

    def list_workflows(self) -> list[ExtractedWorkflow]:
        return self.repository.list_workflows()

    def get_workflow(self, workflow_id: str) -> ExtractedWorkflow:
        workflow = self.repository.get_workflow(workflow_id)
        if workflow is None:
            raise ExtractionNotFoundError(workflow_id)
        return workflow

    def _extract_workflow(self, run_id: str, spec: dict) -> ExtractedWorkflow:
        retrieval = self.retrieval_service.search(
            RetrievalSearchRequest(query=spec["query"], hr_domain=spec["domain"], top_k=4)
        )
        if not retrieval.results:
            retrieval = self.retrieval_service.search(RetrievalSearchRequest(query=spec["query"], top_k=4))

        citations = [_citation(result) for result in retrieval.results if result.similarity > 0]
        if not citations and retrieval.results:
            citations = [_citation(retrieval.results[0])]

        text = "\n".join(result.content for result in retrieval.results)
        confidence = min(0.95, 0.35 + (0.15 * len(citations)) + max((result.similarity for result in retrieval.results), default=0.0))

        return ExtractedWorkflow(
            id=f"wf_{spec['slug']}_{run_id[-6:]}",
            run_id=run_id,
            name=spec["name"],
            description=spec["description"],
            hr_domain=spec["domain"],
            risk_level=_risk_from_text(text, spec["risk_level"]),
            confidence=round(confidence, 3),
            required_inputs=[
                ExtractedRequiredInput(name=name, description=description, sensitive=sensitive, citations=citations[:1])
                for name, description, sensitive in spec["required_inputs"]
            ],
            steps=[
                ExtractedWorkflowStep(order=index, title=title, instruction=instruction, citations=citations[:2])
                for index, (title, instruction) in enumerate(spec["steps"], start=1)
            ],
            policy_rules=_policy_rules(spec, text, citations),
            eligibility_rules=_eligibility_rules(spec, text, citations),
            approval_rules=_approval_rules(text, citations),
            escalation_rules=_escalation_rules(text, citations),
            citations=citations,
        )


def _citation(result: RetrievedChunk) -> ExtractionCitation:
    return ExtractionCitation(
        chunk_id=result.chunk_id,
        source_document_id=result.source_document_id,
        source_title=result.source_title,
        citation_label=result.citation_label,
        excerpt=result.content[:360],
        similarity=result.similarity,
    )


def _risk_from_text(text: str, fallback: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("medical", "fmla", "disability", "harassment", "discrimination", "termination")):
        return "high"
    if any(term in lowered for term in ("payroll", "benefits", "deduction", "salary", "approval")):
        return "medium"
    return fallback


def _policy_rules(spec: dict, text: str, citations: list[ExtractionCitation]) -> list[ExtractedPolicyRule]:
    rules = [
        ExtractedPolicyRule(
            title=f"Use approved {spec['name']} sources",
            rule=f"Answer {spec['name'].lower()} requests using only approved source chunks and cite them.",
            citations=citations,
        )
    ]
    lowered = text.lower()
    if "hris" in lowered:
        rules.append(ExtractedPolicyRule(title="Use HRIS flow", rule="Direct employees to the HRIS process when the source policy requires it.", citations=citations))
    if "do not" in lowered or "should not" in lowered:
        rules.append(ExtractedPolicyRule(title="Respect source restrictions", rule="Preserve explicit source restrictions such as information the employee should not share or actions AI should not take.", citations=citations))
    return rules


def _eligibility_rules(spec: dict, text: str, citations: list[ExtractionCitation]) -> list[ExtractedEligibilityRule]:
    lowered = text.lower()
    rules: list[ExtractedEligibilityRule] = []
    if spec["domain"] in {"benefits", "pto_leave"} or "eligible" in lowered or "eligibility" in lowered:
        rules.append(
            ExtractedEligibilityRule(
                title="Confirm employee applicability",
                rule="Confirm employee type, location, and relevant dates before applying eligibility guidance.",
                citations=citations,
            )
        )
    if "contractor" in lowered:
        rules.append(ExtractedEligibilityRule(title="Contractor applicability", rule="Check whether contractors are excluded from the benefit or policy before answering.", citations=citations))
    return rules


def _approval_rules(text: str, citations: list[ExtractionCitation]) -> list[ExtractedApprovalRule]:
    lowered = text.lower()
    rules: list[ExtractedApprovalRule] = []
    if "approval" in lowered or "approve" in lowered:
        rules.append(
            ExtractedApprovalRule(
                title="Approval required for exceptions",
                condition="The request asks for a policy exception, approval, or decision outside standard guidance.",
                approver_role="HR operations owner",
                citations=citations,
            )
        )
    return rules


def _escalation_rules(text: str, citations: list[ExtractionCitation]) -> list[ExtractedEscalationRule]:
    lowered = text.lower()
    rules: list[ExtractedEscalationRule] = []
    if any(term in lowered for term in ("escalate", "exception", "medical", "fmla", "disability", "compensation")):
        rules.append(
            ExtractedEscalationRule(
                title="Sensitive or exception case",
                trigger="The request involves medical leave, disability accommodation, compensation dispute, protected leave, or a policy exception.",
                destination="HR operations or HR benefits owner",
                citations=citations,
            )
        )
    return rules
