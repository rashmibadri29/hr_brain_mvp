# HR Operations Brain: Tech Stack And Implementation Plan

## Recommended Tech Stack

### Frontend

- **Next.js + React + TypeScript**: Main web app and admin console.
- **Tailwind CSS**: Fast UI styling with predictable design constraints.
- **shadcn/ui or Radix UI**: Accessible components for tables, dialogs, tabs, forms, and review workflows.
- **React Flow**: Workflow and decision-tree visualization.

### Backend

- **Python + FastAPI**: API server for ingestion, extraction, workflow processing, and simulation.
- **Pydantic**: Strong schemas for extracted HR workflows, policy rules, citations, and generated skills.
- **Celery or RQ**: Background jobs for document parsing, chunking, extraction, evaluation, and refresh checks.
- **Redis**: Job queue and short-lived processing state.

### Database And Storage

- **PostgreSQL**: Primary relational database for users, sources, chunks, workflows, policy rules, reviews, versions, and evaluations.
- **pgvector**: Vector search inside Postgres for MVP simplicity.
- **S3-compatible object storage**: Raw uploaded files, parsed text, generated skill files, and exports.
- **Audit log tables**: Track review decisions, approvals, policy changes, and generated skill versions.

### AI And Retrieval

- **OpenAI Responses API**: Core model interface for extraction, classification, summarization, simulation, and skill generation.
- **Structured Outputs**: Use JSON schema-backed extraction so workflows and rules are returned in predictable typed formats.
- **Embeddings**: Generate vectors for document chunks, tickets, policies, and workflow examples.
- **RAG pipeline**: Retrieve source chunks by workflow/topic, then extract structured knowledge with citations.
- **Agents SDK, later phase**: Useful for the agent simulation layer where the model uses skills and internal tools.

### Document Parsing

- **Unstructured.io or LlamaIndex readers**: Parse PDFs, docs, markdown, HTML, and exports.
- **Apache Tika as fallback**: Broad document parsing support.
- **Native CSV/JSON parsers**: Ticket exports, HRIS exports, and workflow fixtures.

### Integrations, MVP First

Start with uploads and exports:

- PDF
- Markdown
- CSV
- JSON
- Google Docs export
- Notion or Confluence export
- Slack or Teams channel export
- HR ticket export

Add live connectors later:

- Google Drive
- Notion
- Confluence
- Slack
- Microsoft Teams
- Jira Service Management
- Zendesk
- Freshservice
- Workday, Rippling, BambooHR, or HiBob

### Security And Governance

- **OAuth/OIDC**: Authentication with Google or Microsoft.
- **Role-based access control**: Admin, reviewer, viewer, employee.
- **PII/sensitive-data labels**: Compensation, medical, leave, employee relations, personally identifiable information.
- **Encryption at rest and in transit**.
- **Audit trail** for every extraction, edit, approval, and skill publication.

### Deployment

- **Vercel**: Frontend deployment.
- **Render, Fly.io, Railway, or AWS ECS**: FastAPI backend.
- **Managed Postgres with pgvector**: Supabase, Neon, RDS, or similar.
- **S3/R2**: File storage.
- **GitHub Actions**: CI checks, tests, migrations, and deployment.

## Core Data Model

MVP tables or collections:

- `organizations`
- `users`
- `source_documents`
- `document_chunks`
- `sensitive_data_findings`
- `hr_workflows`
- `workflow_steps`
- `policy_rules`
- `eligibility_rules`
- `approval_rules`
- `escalation_rules`
- `source_citations`
- `review_items`
- `skill_files`
- `simulation_cases`
- `simulation_results`
- `audit_events`

## Data Collection Strategy

### MVP Collection Method

Use upload and export-based ingestion first. This avoids complex permissions and lets the MVP prove value quickly.

Collect:

- Employee handbook
- Benefits guide
- PTO and leave policy documents
- Onboarding checklists
- Offboarding checklists
- Payroll FAQs
- HR ticket exports
- HR Slack or Teams channel exports
- Internal wiki exports
- Sample employee questions

### Collection Flow

1. HR admin uploads files or exports.
2. System stores raw files in object storage.
3. System records metadata in Postgres:
   - Source type
   - File name
   - Owner
   - Upload time
   - Last updated date, if known
   - Region/country applicability, if known
   - Employee type applicability, if known
4. Parser extracts text and structure.
5. Chunker breaks content into source-preserving chunks.
6. Classifier labels chunks by HR domain and sensitivity.
7. Embedder stores vectors in pgvector.
8. Extraction jobs convert relevant chunks into workflows and rules.

## Processing Pipeline

### 1. Parse

Convert raw files into normalized text and metadata.

Outputs:

- Plain text
- Document sections
- Tables when recoverable
- Source metadata

### 2. Chunk

Split content into source-preserving chunks.

Chunking rules:

- Keep headings attached to body text.
- Keep policy tables intact when possible.
- Keep ticket thread context together.
- Store character offsets or section identifiers for citations.

Outputs:

- `document_chunks`
- Source document reference
- Section title
- Chunk text
- Timestamp and owner metadata

### 3. Classify

Classify each chunk by HR domain, risk level, and sensitivity.

Labels:

- Domain: onboarding, benefits, PTO/leave, payroll, offboarding, compliance, employee records, policy FAQ.
- Risk: low, medium, high.
- Sensitivity: PII, compensation, medical/leave, employee relations, none.

### 4. Retrieve

For each target workflow, retrieve likely relevant chunks using:

- Vector similarity
- Keyword filters
- Source type filters
- HR domain labels
- Freshness filters

### 5. Extract

Use model calls with Structured Outputs to produce typed objects:

- Workflows
- Steps
- Policy rules
- Eligibility rules
- Required inputs
- Approval rules
- Escalation rules
- Source citations
- Confidence scores

### 6. Validate

Programmatically validate extraction outputs:

- Required fields are present.
- Citations point to existing chunks.
- Risk levels are valid.
- High-risk workflows have escalation rules.
- Sensitive topics are not marked as fully automatable.

### 7. Detect Conflicts And Gaps

Compare extracted rules across sources.

Examples:

- Conflicting PTO rollover rules.
- Missing benefits enrollment deadline.
- Payroll issue workflow has no owner.
- Leave workflow lacks region-specific escalation.

### 8. Human Review

Create review items for:

- Draft workflows
- Conflicts
- Missing fields
- High-risk policies
- Proposed skill files

### 9. Publish Skills

Generate skill files only from approved workflows and rules.

Outputs:

- Markdown skill file
- JSON/YAML skill representation
- Version record
- Approval audit event

### 10. Simulate And Evaluate

Run simulated employee requests against generated skills.

Score:

- Correct workflow selection
- Correct required questions
- Correct escalation
- No prohibited advice
- Source-grounded answer

## Phase-Wise Implementation Plan

## Phase 1: MVP Scope And System Foundation

### Goal

Set product boundaries and create the core app foundation.

### Implementation Tasks

- Create Next.js frontend app.
- Create FastAPI backend.
- Set up PostgreSQL with pgvector.
- Add object storage for uploaded files.
- Define Pydantic models for:
  - Source documents
  - Chunks
  - HR workflows
  - Policy rules
  - Review items
  - Skill files
- Define first supported workflows:
  - New hire onboarding
  - PTO and leave policy guidance
  - Payroll issue intake
- Define safety policy:
  - What the AI can answer
  - What requires HR review
  - What must escalate

### Deliverables

- Running web app shell.
- Backend API skeleton.
- Database schema.
- MVP workflow and safety specification.

## Phase 2: HR Knowledge Ingestion

### Goal

Collect HR data from uploads and convert it into searchable chunks.

### Implementation Tasks

- Build upload UI.
- Add backend upload endpoint.
- Store raw files in object storage.
- Create parser jobs for PDF, markdown, CSV, JSON, and text.
- Normalize parsed text.
- Chunk documents with preserved source metadata.
- Save chunks in Postgres.
- Generate embeddings and store them in pgvector.
- Add document/source list UI.

### Deliverables

- Upload flow for HR documents and ticket exports.
- Parsed and chunked HR corpus.
- Searchable chunk store with citations.

## Phase 3: HR Classification And Extraction

### Goal

Turn chunks into structured HR workflows and policy rules.

### Implementation Tasks

- Build chunk classifier:
  - HR domain
  - Risk level
  - Sensitivity label
- Build extraction schemas using Pydantic/JSON Schema:
  - `HRWorkflow`
  - `PolicyRule`
  - `EligibilityRule`
  - `ApprovalRule`
  - `EscalationRule`
  - `RequiredInput`
  - `SourceCitation`
- Use retrieval to gather relevant chunks by workflow.
- Use Structured Outputs to extract typed objects.
- Save draft workflows and policy rules.
- Link every extracted rule to source citations.

### Deliverables

- Draft HR workflows.
- Draft policy and eligibility rules.
- Citation-backed extraction results.

## Phase 4: Risk, Conflict, And Gap Detection

### Goal

Identify unsafe, stale, incomplete, or contradictory HR knowledge.

### Implementation Tasks

- Implement rule comparison:
  - Same topic with different values
  - Same policy with different applicability
  - Same workflow with inconsistent approval rules
- Implement missing-field checks:
  - No owner
  - No escalation path
  - No deadline
  - No employee-type applicability
  - No region applicability where required
- Implement stale-source checks:
  - Missing last-updated date
  - Old handbook version
  - Expired dates
- Implement risk checks:
  - Medical leave must escalate
  - Legal/compliance questions must escalate
  - Compensation disputes must escalate
  - Employee relations must escalate
- Generate review items automatically.

### Deliverables

- Conflict detection engine.
- Gap and stale-content detection.
- HR review queue.

## Phase 5: Human Review Console

### Goal

Let HR admins turn extracted knowledge into approved operating procedure.

### Implementation Tasks

- Build workflow list page.
- Build workflow detail page with:
  - Steps
  - Rules
  - Required inputs
  - Escalation triggers
  - Source citations
  - Confidence/risk labels
- Build conflict review page.
- Add edit forms for workflows and rules.
- Add approve/reject actions.
- Add owner assignment.
- Add version history and audit events.
- Add status lifecycle:
  - Draft
  - Needs review
  - Approved
  - Published
  - Deprecated

### Deliverables

- Admin review console.
- Approved HR workflow records.
- Audit trail for review decisions.

## Phase 6: HR Skill File Generation

### Goal

Generate AI-operable skills from approved workflows.

### Implementation Tasks

- Define skill template sections:
  - Purpose
  - When to use
  - When not to use
  - Required inputs
  - Procedure
  - Eligibility rules
  - Approval rules
  - Escalation triggers
  - Prohibited actions
  - Source citations
  - Examples
- Generate skill markdown from approved workflow records.
- Generate machine-readable JSON/YAML version.
- Add skill preview UI.
- Add publish/version action.
- Store generated skill files in object storage and database.

### Deliverables

- Versioned HR skill files.
- Skill preview and publish flow.
- Download/export endpoints.

## Phase 7: Employee And Agent Simulation

### Goal

Prove that generated skills guide AI behavior safely.

### Implementation Tasks

- Build simulation case library:
  - PTO rollover question
  - New parent leave question
  - Incorrect paycheck question
  - Employment verification request
  - New hire first-day question
  - Resignation/offboarding question
- Build simulator API:
  - Load selected skill file.
  - Provide employee request.
  - Ask model to respond using only the skill and cited sources.
- Add evaluator:
  - Correct workflow selected
  - Required inputs requested
  - Safe escalation
  - No legal/medical/compensation decision
  - Sources cited
- Build simulation UI with score and explanation.

### Deliverables

- Agent simulation page.
- Evaluation scores.
- Demo-ready proof that skills improve HR agent reliability.

## Phase 8: Freshness And Continuous Updates

### Goal

Keep the HR Brain current as documents and tickets change.

### Implementation Tasks

- Add source refresh jobs for uploaded replacement files.
- Detect changed documents by hash.
- Re-parse and re-extract changed sources.
- Compare new extracted rules to approved rules.
- Generate proposed diffs:
  - New rule
  - Changed rule
  - Removed rule
  - New exception
  - Changed escalation owner
- Route proposed updates into review queue.
- Track skill versions and show outdated skills.

### Deliverables

- Update detection.
- Reviewable change proposals.
- Skill freshness indicators.

## MVP Milestone Plan

### Milestone 1: Knowledge Corpus

Build upload, parse, chunk, classify, embed, and search.

### Milestone 2: Structured Brain

Extract workflows, policies, eligibility rules, approval rules, and escalation rules.

### Milestone 3: Review Console

Let HR admins inspect, edit, resolve conflicts, approve workflows, and publish.

### Milestone 4: Skills And Simulation

Generate skill files and test them against realistic employee requests.

### Milestone 5: Living Updates

Detect source changes and propose reviewable updates.

## Practical MVP Cut Line

For the first demo, build only:

- Upload-based ingestion.
- Three workflow types:
  - New hire onboarding
  - PTO and leave guidance
  - Payroll issue intake
- Structured extraction with citations.
- Conflict/gap review queue.
- Human approval.
- Skill file generation.
- Agent simulation and scoring.

Defer:

- Live HRIS integrations.
- Fully automated employee actions.
- Advanced permissions by department.
- Direct Workday/Rippling/BambooHR writes.
- Multi-country legal compliance automation.

