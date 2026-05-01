# Phase 1 MVP Scope And Safety Specification

## Product

HR Operations Brain

## Phase

Phase 1: MVP Scope And System Foundation

## Target Users

- HR operations manager
- People team member
- Office manager
- Employee asking HR questions

## Initial Workflows

### New Hire Onboarding

Risk level: medium

Allowed AI behaviors:

- Collect role, start date, manager, location, and employment type.
- Draft onboarding checklist items.
- Identify missing owner assignments.

Disallowed AI behaviors:

- Create system accounts directly.
- Approve background check or employment eligibility decisions.

### PTO And Leave Guidance

Risk level: high

Allowed AI behaviors:

- Explain approved PTO and leave policy language.
- Ask for employee location, employment type, and leave category.
- Direct employees to the HRIS request flow.

Disallowed AI behaviors:

- Approve or deny leave.
- Provide legal advice.
- Assess medical eligibility.

### Payroll Issue Intake

Risk level: medium

Allowed AI behaviors:

- Collect payroll issue details.
- Classify the issue type.
- Route the request to payroll with a concise intake summary.

Disallowed AI behaviors:

- Change payroll records.
- Promise payment corrections.
- Discuss another employee's pay information.

## Global Safety Policy

Allowed AI behaviors:

- Answer HR policy questions from approved sources.
- Collect required information for HR requests.
- Route requests to the correct HR owner or workflow.
- Generate draft checklists and employee-facing responses.

Disallowed AI behaviors:

- Give legal advice.
- Make employment decisions.
- Approve or deny leave, payroll, benefits, compensation, or termination decisions.
- Handle sensitive employee relations cases autonomously.

Mandatory escalation triggers:

- Medical leave or disability accommodation
- Harassment, discrimination, retaliation, or employee relations issue
- Compensation dispute
- Termination or involuntary offboarding anomaly
- Legal or compliance question
- Policy exception request

## Success Metrics

- Accuracy of extracted policies.
- Percentage of HR tickets correctly classified.
- Reduction in repeated HR questions.
- Human approval rate for generated workflows.
- Number of risky cases correctly escalated.

