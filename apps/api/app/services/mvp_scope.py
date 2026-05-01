from app.models.hr_brain import (
    EscalationRule,
    HRWorkflow,
    MvpScope,
    RequiredInput,
    RiskLevel,
    SafetyPolicy,
    WorkflowStep,
)


def get_mvp_scope() -> MvpScope:
    safety_policy = SafetyPolicy(
        allowed_ai_behaviors=[
            "Answer HR policy questions from approved sources.",
            "Collect required information for HR requests.",
            "Route requests to the correct HR owner or workflow.",
            "Generate draft checklists and employee-facing responses.",
        ],
        disallowed_ai_behaviors=[
            "Give legal advice.",
            "Make employment decisions.",
            "Approve or deny leave, payroll, benefits, compensation, or termination decisions.",
            "Handle sensitive employee relations cases autonomously.",
        ],
        mandatory_escalation_triggers=[
            "Medical leave or disability accommodation",
            "Harassment, discrimination, retaliation, or employee relations issue",
            "Compensation dispute",
            "Termination or involuntary offboarding anomaly",
            "Legal or compliance question",
            "Policy exception request",
        ],
        publication_requirements=[
            "Workflow has a named HR owner.",
            "High-risk workflow has escalation rules.",
            "Every policy rule is linked to at least one source citation.",
            "Workflow has been approved by an HR admin.",
        ],
    )

    workflows = [
        HRWorkflow(
            id="new-hire-onboarding",
            name="New Hire Onboarding",
            description="Create and validate a role-aware onboarding checklist for new employees.",
            risk_level=RiskLevel.medium,
            allowed_ai_behaviors=[
                "Collect role, start date, manager, location, and employment type.",
                "Draft onboarding checklist items.",
                "Identify missing owner assignments.",
            ],
            disallowed_ai_behaviors=[
                "Create system accounts directly.",
                "Approve background check or employment eligibility decisions.",
            ],
            required_inputs=[
                RequiredInput(name="employee_name", description="New hire full name", sensitive=True),
                RequiredInput(name="start_date", description="Expected first day"),
                RequiredInput(name="role", description="Job title or role"),
                RequiredInput(name="manager", description="Hiring manager"),
                RequiredInput(name="location", description="Work location or jurisdiction"),
                RequiredInput(name="employment_type", description="Full-time, part-time, contractor, or intern"),
            ],
            steps=[
                WorkflowStep(order=1, title="Collect onboarding context", instruction="Gather required new hire details."),
                WorkflowStep(order=2, title="Generate checklist", instruction="Draft HR, IT, payroll, and manager tasks."),
                WorkflowStep(order=3, title="Route missing decisions", instruction="Escalate missing owner or eligibility items to HR."),
            ],
            escalation_rules=[
                EscalationRule(
                    title="Missing employment eligibility details",
                    trigger="Employment type, work location, or eligibility status is unclear.",
                    destination="HR operations owner",
                )
            ],
        ),
        HRWorkflow(
            id="pto-leave-guidance",
            name="PTO And Leave Guidance",
            description="Explain approved leave policies and escalate protected, medical, legal, or exception cases.",
            risk_level=RiskLevel.high,
            allowed_ai_behaviors=[
                "Explain approved PTO and leave policy language.",
                "Ask for employee location, employment type, and leave category.",
                "Direct employees to the HRIS request flow.",
            ],
            disallowed_ai_behaviors=[
                "Approve or deny leave.",
                "Provide legal advice.",
                "Assess medical eligibility.",
            ],
            required_inputs=[
                RequiredInput(name="employee_location", description="Employee work location or jurisdiction"),
                RequiredInput(name="employment_type", description="Employee classification"),
                RequiredInput(name="leave_type", description="PTO, sick leave, parental leave, medical leave, or other"),
            ],
            steps=[
                WorkflowStep(order=1, title="Identify applicable policy", instruction="Determine location, employee type, and leave category."),
                WorkflowStep(order=2, title="Answer from approved sources", instruction="Summarize the applicable approved policy with citations."),
                WorkflowStep(order=3, title="Escalate sensitive cases", instruction="Escalate medical, legal, protected leave, or exception requests."),
            ],
            escalation_rules=[
                EscalationRule(
                    title="Protected or medical leave",
                    trigger="Request involves medical leave, accommodation, parental leave, or legally protected leave.",
                    destination="HR benefits or employee relations owner",
                )
            ],
        ),
        HRWorkflow(
            id="payroll-issue-intake",
            name="Payroll Issue Intake",
            description="Collect payroll issue details and route cases without changing payroll records.",
            risk_level=RiskLevel.medium,
            allowed_ai_behaviors=[
                "Collect payroll issue details.",
                "Classify the issue type.",
                "Route the request to payroll with a concise intake summary.",
            ],
            disallowed_ai_behaviors=[
                "Change payroll records.",
                "Promise payment corrections.",
                "Discuss another employee's pay information.",
            ],
            required_inputs=[
                RequiredInput(name="pay_period", description="Affected pay period"),
                RequiredInput(name="issue_type", description="Missing pay, incorrect amount, deduction issue, tax issue, or other"),
                RequiredInput(name="employee_summary", description="Employee's description of the issue", sensitive=True),
            ],
            steps=[
                WorkflowStep(order=1, title="Collect issue details", instruction="Gather pay period, issue type, and employee description."),
                WorkflowStep(order=2, title="Classify urgency", instruction="Identify whether the issue blocks rent, benefits, or legal deadlines."),
                WorkflowStep(order=3, title="Route to payroll", instruction="Send a structured intake summary to the payroll owner."),
            ],
            escalation_rules=[
                EscalationRule(
                    title="Compensation dispute",
                    trigger="Employee disputes pay rate, bonus, equity, or compensation decision.",
                    destination="Payroll and HR operations owner",
                )
            ],
        ),
    ]

    return MvpScope(
        product_name="HR Operations Brain",
        phase="Phase 1: MVP Scope And System Foundation",
        workflows=workflows,
        safety_policy=safety_policy,
        success_metrics=[
            "Accuracy of extracted policies.",
            "Percentage of HR tickets correctly classified.",
            "Reduction in repeated HR questions.",
            "Human approval rate for generated workflows.",
            "Number of risky cases correctly escalated.",
        ],
    )

