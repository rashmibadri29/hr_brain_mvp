# HR Operations Brain MVP Plan

## Concept

An HR Operations Brain turns scattered HR policies, handbooks, tickets, onboarding docs, payroll rules, and people-operations knowledge into approved, executable workflows that AI agents can safely use to support employees and HR teams.

The MVP should prove that messy HR knowledge can become trusted operating procedure:

**Scattered HR docs and tickets go in. Approved HR workflows and AI-ready skills come out.**

## Recommended MVP Scope

Start with workflows that are common, repeatable, and valuable, while avoiding highly sensitive autonomous decisions.

Recommended first workflows:

- New hire onboarding
- PTO and leave policy guidance
- Benefits eligibility FAQ
- Payroll issue intake
- Offboarding checklist

Avoid early automation for:

- Termination decisions
- Compensation changes
- Legal advice
- Performance management decisions
- Sensitive employee relations cases
- Medical or disability accommodations without human escalation

## Phase 1: MVP Scope And Success Criteria

### Goal

Define the first HR workflows, users, allowed behaviors, safety boundaries, and success metrics.

### Tasks

- Choose 3-5 initial workflows:
  - New hire onboarding
  - PTO and leave policy guidance
  - Benefits eligibility FAQ
  - Payroll issue intake
  - Offboarding checklist
- Define target users:
  - HR operations manager
  - People team
  - Office manager
  - Employees asking HR questions
- Define allowed AI behaviors:
  - Answer policy questions from approved sources
  - Collect required information
  - Route requests
  - Generate checklists
  - Draft HR responses
- Define disallowed AI behaviors:
  - Giving legal advice
  - Making employment decisions
  - Approving leave or pay changes without authorization
  - Handling sensitive employee relations cases autonomously
- Set MVP success metrics:
  - Accuracy of extracted policies
  - Percentage of HR tickets correctly classified
  - Reduction in repeated HR questions
  - Human approval rate for generated workflows
  - Number of risky cases correctly escalated

### Deliverable

HR Operations Brain MVP spec with selected workflows, users, risks, and success metrics.

## Phase 2: HR Knowledge Ingestion

### Goal

Bring fragmented HR knowledge into one processing layer.

### Tasks

- Support file and export-based ingestion first:
  - Employee handbook
  - Benefits guides
  - PTO and leave policies
  - Onboarding docs
  - Offboarding checklists
  - Payroll FAQ docs
  - HR ticket exports
  - Slack or Teams HR channel exports
  - Notion, Confluence, or Google Docs exports
- Parse and chunk documents.
- Preserve metadata:
  - Source name
  - Owner
  - Last updated date
  - Region or country applicability
  - Employee type applicability
  - Source link or file name
- Classify knowledge by HR domain:
  - Onboarding
  - Benefits
  - PTO and leave
  - Payroll
  - Compliance
  - Offboarding
  - Employee records
  - Policy FAQ
- Flag sensitive data:
  - Compensation
  - Medical or leave details
  - Employee relations
  - Personally identifiable information

### Deliverable

Searchable, attributed HR knowledge corpus with source metadata and sensitivity labels.

## Phase 3: HR Workflow And Policy Extraction

### Goal

Convert messy HR docs and tickets into structured operating knowledge.

### Tasks

- Extract structured HR objects:
  - `HRWorkflow`
  - `PolicyRule`
  - `EligibilityRule`
  - `RequiredInput`
  - `ApprovalRule`
  - `EscalationRule`
  - `Jurisdiction`
  - `EmployeeType`
  - `SourceCitation`
  - `Owner`
- Extract important details:
  - Who is eligible
  - Required forms
  - Required approvals
  - Deadlines
  - Regional differences
  - Employee type differences
  - Exceptions
  - Escalation paths
- Generate workflow drafts:
  - New hire setup checklist
  - PTO request guidance
  - Benefits enrollment flow
  - Payroll issue triage
  - Offboarding sequence

### Deliverable

Structured HR workflows and policy rules with citations back to original sources.

## Phase 4: Risk, Conflict, And Gap Detection

### Goal

Identify where HR knowledge is unsafe, incomplete, outdated, or contradictory.

### Tasks

- Detect conflicts:
  - One policy says PTO rolls over.
  - Another policy says unused PTO expires.
  - Benefits eligibility differs across docs.
- Detect missing information:
  - No owner for payroll escalation.
  - No deadline for benefits enrollment.
  - No location-specific leave rule.
- Detect outdated content:
  - Old benefits provider names
  - Outdated handbook versions
  - Expired enrollment dates
- Assign risk levels:
  - Low: office policy FAQ
  - Medium: payroll or benefits routing
  - High: leave, accommodations, employee relations, termination
- Define mandatory escalation triggers:
  - Legal or compliance questions
  - Medical leave
  - Harassment or discrimination
  - Compensation disputes
  - Termination or offboarding anomalies

### Deliverable

Review queue showing HR conflicts, stale policies, missing fields, and high-risk areas.

## Phase 5: Human Review Console

### Goal

Let HR admins approve, correct, and govern the brain.

### Tasks

- Build admin views:
  - Workflow list
  - Policy rules
  - Conflicts and gaps
  - Source citations
  - Risk levels
  - Skill preview
- Allow HR admins to:
  - Approve workflows
  - Edit extracted rules
  - Resolve contradictions
  - Assign policy owners
  - Set region and employee-type applicability
  - Mark content as current or stale
  - Publish approved skills
- Add governance:
  - Approval status
  - Version history
  - Last reviewed date
  - Reviewer identity
  - Change notes

### Deliverable

HR review console where extracted knowledge becomes trusted operating procedure.

## Phase 6: HR Skill File Generation

### Goal

Turn approved HR workflows into AI-executable skill files.

### Tasks

- Generate skill files for each approved workflow.
- Include:
  - Purpose
  - When to use
  - When not to use
  - Required employee inputs
  - Step-by-step process
  - Eligibility rules
  - Approval rules
  - Escalation triggers
  - Prohibited actions
  - Required citations
  - Example employee requests
  - Expected outcomes
- Add guardrails:
  - Do not provide legal advice.
  - Do not make compensation decisions.
  - Do not approve or deny leave.
  - Escalate medical, legal, discrimination, or termination-related matters.
  - Use only approved policy sources.
  - Cite relevant policy sources in answers.

### Deliverable

Versioned HR operations skill files usable by AI agents.

### Example Skill Output

```markdown
# PTO Policy Guidance Skill

## When to use

Use when an employee asks about PTO balance, accrual, rollover, or request process.

## Required inputs

- Employee location
- Employee type
- Requested dates
- Whether leave is PTO, sick leave, parental leave, or another type

## Procedure

1. Identify employee location and employee type.
2. Determine applicable policy.
3. Explain eligibility and request process.
4. Direct employee to the HRIS request flow.
5. Escalate if the request involves medical leave, legal protection, or policy exception.

## Never do

- Do not approve or deny leave.
- Do not provide legal advice.
- Do not discuss another employee's leave status.
```

## Phase 7: Employee And Agent Simulation

### Goal

Prove that the generated HR Brain improves AI responses and workflow handling.

### Tasks

- Create simulated employee requests:
  - "How much PTO can I carry over?"
  - "I just had a baby. What leave do I get?"
  - "My paycheck is wrong."
  - "I need an employment verification letter."
  - "What happens on my first day?"
  - "I am leaving the company next month."
- Have the AI agent use generated HR skills.
- Evaluate whether the agent:
  - Selects the right workflow
  - Asks required questions
  - Uses the correct policy
  - Avoids unsafe advice
  - Escalates sensitive cases
  - Cites sources
- Score results:
  - Correct policy application
  - Safe escalation
  - Completeness
  - Source grounding
  - Employee clarity

### Deliverable

Demo simulator proving the HR Brain can guide AI agents safely and consistently.

## Phase 8: Freshness And Continuous Updates

### Goal

Keep HR knowledge current over time.

### Tasks

- Detect new or changed source material:
  - Updated handbook
  - New benefits guide
  - New payroll FAQ
  - New HR tickets
- Propose updates:
  - Policy change
  - New exception
  - New recurring question
  - Changed escalation owner
- Compare ticket behavior against approved workflows.
- Generate reviewable diffs:
  - "Update benefits enrollment deadline"
  - "Add California-specific leave escalation"
  - "Replace old payroll provider reference"
- Notify policy owners for approval.

### Deliverable

Living update loop for HR workflows and skill files.

## Recommended MVP Build Order

1. Upload HR docs and ticket exports.
2. Extract workflows, policies, eligibility rules, and escalation rules.
3. Show source citations and confidence scores.
4. Flag conflicts, gaps, outdated docs, and high-risk topics.
5. Let HR admins review and approve.
6. Generate HR skill files.
7. Run employee request simulations.
8. Show evaluation results and improvement areas.

## Best First Demo Workflows

### 1. New Hire Onboarding

Shows checklist generation, owner assignment, and multi-step workflow extraction.

### 2. PTO And Leave Policy Guidance

Shows eligibility rules, location differences, and escalation safety.

### 3. Payroll Issue Intake

Shows employee information collection, routing, and clear boundaries without directly changing payroll.

