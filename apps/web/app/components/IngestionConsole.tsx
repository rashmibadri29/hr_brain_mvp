"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";

type SourceDocument = {
  id: string;
  title: string;
  original_filename: string;
  source_type: string;
  content_type: string | null;
  storage_path: string;
  processing_status: string;
  uploaded_by: string | null;
  uploaded_at: string;
  processed_at: string | null;
  error_message: string | null;
  chunk_count: number;
  detected_domains: string[];
  sensitivity_labels: string[];
};

type DocumentChunk = {
  id: string;
  source_document_id: string;
  source_title: string;
  chunk_index: number;
  content: string;
  section_title: string | null;
  start_char: number;
  end_char: number;
  hr_domain: string;
  risk_level: string;
  sensitivity_label: string;
  citation_label: string;
  created_at: string;
};

type SourceDetail = SourceDocument & {
  chunks: DocumentChunk[];
};

type IngestionSummary = {
  source_count: number;
  chunk_count: number;
  parsed_count: number;
  failed_count: number;
  supported_file_types: string[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const sourceTypes = [
  ["employee_handbook", "Employee handbook"],
  ["benefits_guide", "Benefits guide"],
  ["pto_leave_policy", "PTO/leave policy"],
  ["onboarding_doc", "Onboarding doc"],
  ["offboarding_checklist", "Offboarding checklist"],
  ["payroll_faq", "Payroll FAQ"],
  ["hr_ticket_export", "HR ticket export"],
  ["hr_channel_export", "HR channel export"],
  ["internal_wiki", "Internal wiki"],
  ["other", "Other"]
];

export function IngestionConsole() {
  const [summary, setSummary] = useState<IngestionSummary | null>(null);
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [selectedSource, setSelectedSource] = useState<SourceDetail | null>(null);
  const [title, setTitle] = useState("");
  const [sourceType, setSourceType] = useState("other");
  const [uploadedBy, setUploadedBy] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedSourceId = selectedSource?.id;

  async function refreshSources(nextSelectedId?: string) {
    const [summaryResponse, sourcesResponse] = await Promise.all([
      fetch(`${API_BASE}/api/v1/sources/summary`),
      fetch(`${API_BASE}/api/v1/sources`)
    ]);

    if (!summaryResponse.ok || !sourcesResponse.ok) {
      throw new Error("Unable to load ingestion sources from the API.");
    }

    const nextSummary = (await summaryResponse.json()) as IngestionSummary;
    const nextSources = (await sourcesResponse.json()) as SourceDocument[];
    setSummary(nextSummary);
    setSources(nextSources);

    const sourceToSelect = nextSelectedId ?? selectedSourceId ?? nextSources[0]?.id;
    if (sourceToSelect) {
      await loadSource(sourceToSelect);
    } else {
      setSelectedSource(null);
    }
  }

  async function loadSource(sourceId: string) {
    const response = await fetch(`${API_BASE}/api/v1/sources/${sourceId}`);
    if (!response.ok) {
      throw new Error("Unable to load source detail.");
    }
    setSelectedSource((await response.json()) as SourceDetail);
  }

  useEffect(() => {
    refreshSources().catch((caught: unknown) => {
      setError(caught instanceof Error ? caught.message : "Unable to load ingestion data.");
    });
    // This should run only once on mount; refreshSources manages selected state internally.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Choose a file before uploading.");
      return;
    }

    setIsUploading(true);
    setError(null);

    const payload = new FormData();
    payload.append("file", file);
    payload.append("source_type", sourceType);
    if (title.trim()) {
      payload.append("title", title.trim());
    }
    if (uploadedBy.trim()) {
      payload.append("uploaded_by", uploadedBy.trim());
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1/sources`, {
        method: "POST",
        body: payload
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || "Upload failed.");
      }

      const detail = (await response.json()) as SourceDetail;
      setTitle("");
      setSourceType("other");
      setUploadedBy("");
      setFile(null);
      const input = document.getElementById("source-file") as HTMLInputElement | null;
      if (input) {
        input.value = "";
      }
      await refreshSources(detail.id);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  const supportedTypes = useMemo(
    () => summary?.supported_file_types.join(", ") ?? ".txt, .md, .csv, .json",
    [summary]
  );

  return (
    <section className="ingestionPanel" aria-labelledby="ingestion-title">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Phase 2</p>
          <h2 id="ingestion-title">HR Knowledge Ingestion</h2>
        </div>
        <div className="summaryStrip" aria-label="Ingestion summary">
          <SummaryStat label="Sources" value={summary?.source_count ?? 0} />
          <SummaryStat label="Chunks" value={summary?.chunk_count ?? 0} />
          <SummaryStat label="Parsed" value={summary?.parsed_count ?? 0} />
          <SummaryStat label="Failed" value={summary?.failed_count ?? 0} />
        </div>
      </div>

      <div className="ingestionGrid">
        <form className="uploadForm" onSubmit={handleUpload}>
          <label>
            Source title
            <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="2026 Employee Handbook" />
          </label>
          <label>
            Source type
            <select value={sourceType} onChange={(event) => setSourceType(event.target.value)}>
              {sourceTypes.map(([value, label]) => (
                <option value={value} key={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Uploaded by
            <input value={uploadedBy} onChange={(event) => setUploadedBy(event.target.value)} placeholder="hr@example.com" />
          </label>
          <label>
            File
            <input id="source-file" type="file" accept=".txt,.md,.csv,.json" onChange={handleFileChange} />
          </label>
          <button type="submit" disabled={isUploading}>
            {isUploading ? "Processing..." : "Upload Source"}
          </button>
          <p className="formHint">Supported for MVP: {supportedTypes}</p>
          {error ? <p className="errorText">{error}</p> : null}
        </form>

        <div className="sourceList" aria-label="Uploaded sources">
          {sources.length === 0 ? (
            <div className="emptyState">No HR sources uploaded yet.</div>
          ) : (
            sources.map((source) => (
              <button
                className={source.id === selectedSource?.id ? "sourceButton active" : "sourceButton"}
                key={source.id}
                onClick={() => {
                  loadSource(source.id).catch((caught: unknown) => {
                    setError(caught instanceof Error ? caught.message : "Unable to load source.");
                  });
                }}
                type="button"
              >
                <span>{source.title}</span>
                <small>
                  {source.processing_status} · {source.chunk_count} chunks
                </small>
              </button>
            ))
          )}
        </div>
      </div>

      {selectedSource ? <SourcePreview source={selectedSource} /> : null}
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

function SourcePreview({ source }: { source: SourceDetail }) {
  return (
    <div className="sourcePreview">
      <div className="sourceMeta">
        <div>
          <h3>{source.title}</h3>
          <p>{source.original_filename}</p>
        </div>
        <div className="badges inline">
          <span>{source.source_type.replaceAll("_", " ")}</span>
          <span>{source.processing_status}</span>
        </div>
      </div>

      {source.error_message ? <p className="errorText">{source.error_message}</p> : null}

      <div className="chunkList">
        {source.chunks.length === 0 ? (
          <div className="emptyState">No chunks available for this source.</div>
        ) : (
          source.chunks.map((chunk) => (
            <article className="chunkCard" key={chunk.id}>
              <header>
                <div>
                  <strong>{chunk.citation_label}</strong>
                  {chunk.section_title ? <span>{chunk.section_title}</span> : null}
                </div>
                <div className="badges inline">
                  <span>{chunk.hr_domain.replaceAll("_", " ")}</span>
                  <span>{chunk.risk_level}</span>
                  <span>{chunk.sensitivity_label.replaceAll("_", " ")}</span>
                </div>
              </header>
              <p>{chunk.content}</p>
            </article>
          ))
        )}
      </div>
    </div>
  );
}
