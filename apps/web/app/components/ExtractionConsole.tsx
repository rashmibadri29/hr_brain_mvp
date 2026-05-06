"use client";

import { useEffect, useMemo, useState } from "react";

type EmbeddingSummary = {
  embedding_count: number;
  chunk_count: number;
  missing_count: number;
  embedding_model: string;
  dimensions: number;
};

type ExtractionSummary = {
  run_count: number;
  workflow_count: number;
  latest_run_id: string | null;
  latest_run_at: string | null;
};

type ExtractionCitation = {
  chunk_id: string;
  source_document_id: string;
  source_title: string;
  citation_label: string;
  excerpt: string;
  similarity: number | null;
};

type ExtractedWorkflow = {
  id: string;
  run_id: string;
  name: string;
  description: string;
  hr_domain: string;
  risk_level: string;
  confidence: number;
  required_inputs: { name: string; description: string; sensitive: boolean }[];
  steps: { order: number; title: string; instruction: string }[];
  policy_rules: { title: string; rule: string }[];
  eligibility_rules: { title: string; rule: string }[];
  approval_rules: { title: string; condition: string; approver_role: string }[];
  escalation_rules: { title: string; trigger: string; destination: string }[];
  citations: ExtractionCitation[];
  created_at: string;
};

type ExtractionRunDetail = {
  id: string;
  status: string;
  workflow_count: number;
  chunk_count: number;
  created_at: string;
  error_message: string | null;
  workflows: ExtractedWorkflow[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export function ExtractionConsole() {
  const [embeddingSummary, setEmbeddingSummary] = useState<EmbeddingSummary | null>(null);
  const [extractionSummary, setExtractionSummary] = useState<ExtractionSummary | null>(null);
  const [workflows, setWorkflows] = useState<ExtractedWorkflow[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedWorkflow = useMemo(
    () => workflows.find((workflow) => workflow.id === selectedWorkflowId) ?? workflows[0] ?? null,
    [selectedWorkflowId, workflows]
  );

  async function refreshExtractionState() {
    const [embeddingResponse, extractionResponse, workflowsResponse] = await Promise.all([
      fetch(`${API_BASE}/api/v1/embeddings/summary`),
      fetch(`${API_BASE}/api/v1/extractions/summary`),
      fetch(`${API_BASE}/api/v1/extractions/workflows`)
    ]);

    if (!embeddingResponse.ok || !extractionResponse.ok || !workflowsResponse.ok) {
      throw new Error("Unable to load extraction state from the API.");
    }

    setEmbeddingSummary((await embeddingResponse.json()) as EmbeddingSummary);
    setExtractionSummary((await extractionResponse.json()) as ExtractionSummary);
    const nextWorkflows = (await workflowsResponse.json()) as ExtractedWorkflow[];
    setWorkflows(nextWorkflows);
    if (!selectedWorkflowId && nextWorkflows[0]) {
      setSelectedWorkflowId(nextWorkflows[0].id);
    }
  }

  useEffect(() => {
    refreshExtractionState().catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Unable to load extraction state.");
    });
    // Run once on mount; user actions explicitly refresh state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function rebuildEmbeddings() {
    setError(null);
    const response = await fetch(`${API_BASE}/api/v1/embeddings/rebuild`, { method: "POST" });
    if (!response.ok) {
      throw new Error("Embedding rebuild failed.");
    }
    await refreshExtractionState();
  }

  async function runExtraction() {
    setIsRunning(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/v1/extractions/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rebuild_embeddings: true })
      });
      if (!response.ok) {
        throw new Error("Extraction run failed.");
      }
      const detail = (await response.json()) as ExtractionRunDetail;
      setWorkflows(detail.workflows);
      setSelectedWorkflowId(detail.workflows[0]?.id ?? null);
      await refreshExtractionState();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Extraction run failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <section className="ingestionPanel" aria-labelledby="extraction-title">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Phase 3</p>
          <h2 id="extraction-title">Workflow Extraction</h2>
        </div>
        <div className="summaryStrip" aria-label="Extraction summary">
          <SummaryStat label="Embeddings" value={embeddingSummary?.embedding_count ?? 0} />
          <SummaryStat label="Missing" value={embeddingSummary?.missing_count ?? 0} />
          <SummaryStat label="Runs" value={extractionSummary?.run_count ?? 0} />
          <SummaryStat label="Workflows" value={extractionSummary?.workflow_count ?? 0} />
        </div>
      </div>

      <div className="actionRow">
        <button type="button" onClick={() => rebuildEmbeddings().catch((caught) => setError(caught.message))}>
          Rebuild Embeddings
        </button>
        <button type="button" onClick={runExtraction} disabled={isRunning}>
          {isRunning ? "Extracting..." : "Run Extraction"}
        </button>
        <span>{embeddingSummary ? `${embeddingSummary.embedding_model}, ${embeddingSummary.dimensions} dimensions` : "Local embeddings"}</span>
      </div>
      {error ? <p className="errorText">{error}</p> : null}

      <div className="extractionGrid">
        <div className="sourceList" aria-label="Extracted workflows">
          {workflows.length === 0 ? (
            <div className="emptyState">No extracted workflows yet.</div>
          ) : (
            workflows.map((workflow) => (
              <button
                className={workflow.id === selectedWorkflow?.id ? "sourceButton active" : "sourceButton"}
                key={workflow.id}
                onClick={() => setSelectedWorkflowId(workflow.id)}
                type="button"
              >
                <span>{workflow.name}</span>
                <small>
                  {workflow.hr_domain.replaceAll("_", " ")} · {workflow.risk_level} · {Math.round(workflow.confidence * 100)}%
                </small>
              </button>
            ))
          )}
        </div>

        {selectedWorkflow ? <WorkflowPreview workflow={selectedWorkflow} /> : null}
      </div>
    </section>
  );
}

function SummaryStat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function WorkflowPreview({ workflow }: { workflow: ExtractedWorkflow }) {
  return (
    <article className="workflowPreview">
      <header>
        <div>
          <h3>{workflow.name}</h3>
          <p>{workflow.description}</p>
        </div>
        <div className="badges inline">
          <span>{workflow.hr_domain.replaceAll("_", " ")}</span>
          <span>{workflow.risk_level}</span>
          <span>{Math.round(workflow.confidence * 100)}% confidence</span>
        </div>
      </header>

      <PreviewSection title="Steps" items={workflow.steps.map((step) => `${step.order}. ${step.title}: ${step.instruction}`)} />
      <PreviewSection title="Required Inputs" items={workflow.required_inputs.map((input) => `${input.name}: ${input.description}`)} />
      <PreviewSection title="Policy Rules" items={workflow.policy_rules.map((rule) => `${rule.title}: ${rule.rule}`)} />
      <PreviewSection title="Eligibility Rules" items={workflow.eligibility_rules.map((rule) => `${rule.title}: ${rule.rule}`)} />
      <PreviewSection title="Approval Rules" items={workflow.approval_rules.map((rule) => `${rule.title}: ${rule.condition} (${rule.approver_role})`)} />
      <PreviewSection title="Escalation Rules" items={workflow.escalation_rules.map((rule) => `${rule.title}: ${rule.trigger} -> ${rule.destination}`)} />

      <div className="citationList">
        <h4>Citations</h4>
        {workflow.citations.map((citation) => (
          <div key={citation.chunk_id}>
            <strong>{citation.citation_label}</strong>
            <span>{citation.source_title}</span>
            <p>{citation.excerpt}</p>
          </div>
        ))}
      </div>
    </article>
  );
}

function PreviewSection({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) {
    return null;
  }
  return (
    <section className="previewSection">
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
