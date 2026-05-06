import { ExtractionConsole } from "./components/ExtractionConsole";
import { IngestionConsole } from "./components/IngestionConsole";

const workflows = [
  {
    name: "New Hire Onboarding",
    risk: "Medium",
    status: "Defined",
    summary: "Generate role-aware onboarding checklists and route missing owner decisions to HR."
  },
  {
    name: "PTO And Leave Guidance",
    risk: "High",
    status: "Defined",
    summary: "Explain approved leave policies while escalating medical, legal, and exception cases."
  },
  {
    name: "Payroll Issue Intake",
    risk: "Medium",
    status: "Defined",
    summary: "Collect required payroll issue details and route cases without changing payroll records."
  }
];

const phases = [
  "Scope and system foundation",
  "HR knowledge ingestion",
  "Classification and extraction",
  "Risk, conflict, and gap detection",
  "Human review console",
  "Skill file generation",
  "Employee and agent simulation",
  "Freshness and updates"
];

export default function Home() {
  return (
    <main className="shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Phase 3 extraction</p>
          <h1>HR Operations Brain</h1>
          <p className="lede">
            Convert scattered HR policies, tickets, and onboarding knowledge into approved workflows and
            AI-ready operating skills.
          </p>
        </div>
        <div className="statusPanel" aria-label="MVP status">
          <span>Current milestone</span>
          <strong>Classification and extraction</strong>
          <p>Embed source chunks, retrieve semantically relevant knowledge, and draft structured HR workflows.</p>
        </div>
      </section>

      <IngestionConsole />

      <ExtractionConsole />

      <section className="grid two">
        <div className="panel">
          <h2>MVP Workflows</h2>
          <div className="workflowList">
            {workflows.map((workflow) => (
              <article className="workflow" key={workflow.name}>
                <div>
                  <h3>{workflow.name}</h3>
                  <p>{workflow.summary}</p>
                </div>
                <div className="badges">
                  <span>{workflow.risk}</span>
                  <span>{workflow.status}</span>
                </div>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Build Phases</h2>
          <ol className="phaseList">
            {phases.map((phase, index) => (
              <li key={phase}>
                <span>{index + 1}</span>
                {phase}
              </li>
            ))}
          </ol>
        </div>
      </section>
    </main>
  );
}

