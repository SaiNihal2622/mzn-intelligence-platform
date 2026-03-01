import { useState } from 'react';
import Sidebar from './components/Sidebar';
import InputPanel from './components/InputPanel';
import ResultsDashboard from './components/ResultsDashboard';
import { analyzeProject } from './services/api';

function App() {
  const [activeTab, setActiveTab] = useState('analysis');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleAnalysis = async (formData) => {
    setIsAnalyzing(true);
    setError(null);
    setResults(null);
    try {
      const data = await analyzeProject(formData);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        <header className="mb-8">
          <h1 className="text-2xl font-bold">Project Analysis Workspace</h1>
          <p className="text-sm text-muted mt-2">
            Run multi-agent AI pipelines to generate funding matches, knowledge retrieval, and proposal architectures.
          </p>
        </header>

        {activeTab === 'analysis' && (
          <div style={{ maxWidth: '1024px', margin: '0 auto' }} className="space-y-8">
            <InputPanel onSubmit={handleAnalysis} isAnalyzing={isAnalyzing} />

            {error && (
              <div className="error-banner">
                Error: {error}
              </div>
            )}

            {results && <ResultsDashboard results={results} />}
          </div>
        )}

        {activeTab === 'architecture' && (
          <div className="space-y-6" style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <div className="glass-panel" style={{ padding: '2.5rem' }}>
              <h2 className="text-2xl font-bold mb-6 text-slate-800" style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '1rem' }}>
                🏗️ System Architecture & Workflow
              </h2>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-3">1. Architecture Philosophy</h3>
                <p className="text-slate-600 leading-relaxed">
                  The Development Intelligence Platform is intentionally designed as a structured, **multi-agent orchestration system**, rather than a conversational chatbot. Development consultancies require predictable outputs, structured documentation, and workflow reproducibility. The system abandons conversational LLM chat in favor of a deterministic sequential pipeline.
                </p>
              </section>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-3">2. System Overview</h3>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 font-mono text-sm overflow-x-auto">
                  <pre>{`
React Dashboard (Frontend)
    ↓
FastAPI Backend (POST /analyze-project)
    ↓
Agent Orchestrator (Sequential Execution)
    1. PlannerAgent
    2. KnowledgeAgent  → FAISS Vector Store
    3. FundingAgent    → Structured CSV Dataset
    4. ProposalAgent
    5. WorkflowAgent
    6. ComplianceAgent
    ↓
Aggregated Structured JSON Payload
                  `}</pre>
                </div>
              </section>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-4">3. Agent Roles</h3>
                <div className="grid-2 gap-4">
                  {[
                    { name: 'PlannerAgent', role: 'Engagement Lead', desc: 'Frames the consultancy brief and defines priorities.' },
                    { name: 'KnowledgeAgent', role: 'Research Analyst', desc: 'Retrieves institutional best practices via RAG.' },
                    { name: 'FundingAgent', role: 'Grants Specialist', desc: 'Cross-matches projects against donor datasets.' },
                    { name: 'ProposalAgent', role: 'Technical Writer', desc: 'Generates structured strategies and briefings.' },
                    { name: 'WorkflowAgent', role: 'Project Manager', desc: 'Produces actionable sprint task checklists.' },
                    { name: 'ComplianceAgent', role: 'QA/Legal Lead', desc: 'Validates GDPR and ethical standards.' },
                  ].map((agent) => (
                    <div key={agent.name} className="card-item p-4 border border-slate-200 rounded-lg bg-white shadow-sm">
                      <h4 className="font-bold text-slate-800">{agent.name}</h4>
                      <p className="text-xs font-semibold text-blue-600 mb-2">Analogy: {agent.role}</p>
                      <p className="text-sm text-slate-600">{agent.desc}</p>
                    </div>
                  ))}
                </div>
              </section>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-3">4. Intelligence Layer</h3>
                <p className="text-slate-600 mb-4">
                  The platform utilizes a **local vector store** and **semantic embeddings** to ensure data privacy and fast retrieval.
                </p>
                <div className="grid-2 gap-4">
                  <div className="card-item bg-slate-50 border-slate-200">
                    <h5 className="font-bold text-slate-700 mb-1">FAISS Index</h5>
                    <p className="text-xs text-slate-500">In-memory RAM-based vector index for lightning-fast similarity search.</p>
                  </div>
                  <div className="card-item bg-slate-50 border-slate-200">
                    <h5 className="font-bold text-slate-700 mb-1">all-MiniLM-L6-v2</h5>
                    <p className="text-xs text-slate-500">Local embedding model ensuring zero third-party exposure of sensitive data.</p>
                  </div>
                </div>
              </section>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-3">5. Sequential Orchestration</h3>
                <p className="text-slate-600 leading-relaxed">
                  Deterministic pipelines are preferred over conversational AI to ensure that the consultancy output remains high-quality and consistent. Each agent has a clear responsibility and passes its output to the next stage in the pipeline.
                </p>
              </section>

              <section className="mb-10">
                <h3 className="text-lg font-bold text-blue-800 mb-3">6. Scalability with APIs</h3>
                <p className="text-slate-600 leading-relaxed">
                  The architecture is **LLM-agnostic**. By simply swapping the provider in the configuration, the system can leverage high-reasoning frontier models (Gemini 1.5 Pro, Claude 3.5 Sonnet) with zero changes to the core agent logic.
                </p>
              </section>

              <section className="mb-4">
                <h3 className="text-lg font-bold text-blue-800 mb-3">7. Responsible AI</h3>
                <p className="text-slate-600 leading-relaxed">
                  The platform implements human-in-the-loop validation, GDPR data protections, and ethical representation checklists as mandatory pipeline steps.
                </p>
              </section>
            </div>
          </div>
        )}

        {activeTab === 'workflow' && (
          <div className="space-y-6" style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <div className="glass-panel" style={{ padding: '2.5rem' }}>
              <h2 className="text-2xl font-bold mb-6 text-slate-800" style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '1rem' }}>
                📊 Deep Workflow Analysis
              </h2>

              <div className="space-y-10">
                <section>
                  <h3 className="text-xl font-bold text-slate-700 mb-4 italic">The Consultancy Intelligence Divide</h3>
                  <p className="text-slate-600 leading-relaxed mb-6">
                    International development consultancies face an **"Intelligence Divide."** On one side is a massive repository of fragmented institutional memory (thousands of project reports). On the other is the pressurized project cycle where consultants must deliver evidence-based strategies in days. The Development Intelligence Platform bridges this divide using **multi-agent orchestration**.
                  </p>
                </section>

                <section>
                  <h4 className="font-bold text-slate-800 mb-6 bg-slate-50 p-3 rounded-lg border-l-4 border-blue-500">Agentic Augmentation: From Research to Advisory</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                      { role: 'Engagement Lead', counter: 'PlannerAgent', benefit: 'Scoping: Translates client needs into a technical framework.' },
                      { role: 'Research Analyst', counter: 'KnowledgeAgent', benefit: 'Memory: Instantly retrieves exact paragraphs from a decade of reports.' },
                      { role: 'Grants Specialist', counter: 'FundingAgent', benefit: 'Alignment: Deterministically matches donor criteria against the brief.' },
                      { role: 'Strategy Director', counter: 'ProposalAgent', benefit: 'Synthesis: Generates the "Draft Zero" technical strategy.' },
                      { role: 'Project Manager', counter: 'WorkflowAgent', benefit: 'Velocity: Translates strategy into a granular 2-sprint plan.' },
                      { role: 'Compliance Lead', counter: 'ComplianceAgent', benefit: 'Integrity: Validates GDPR and Ethical standards regionally.' },
                    ].map((item) => (
                      <div key={item.role} className="card-item p-4 border border-slate-100 rounded-xl bg-white shadow-sm hover:shadow-md transition-shadow">
                        <h5 className="font-bold text-blue-800 mb-1">{item.role}</h5>
                        <p className="text-[10px] uppercase font-bold text-slate-400 mb-2">Counterpart: {item.counter}</p>
                        <p className="text-sm text-slate-600 leading-relaxed">{item.benefit}</p>
                      </div>
                    ))}
                  </div>
                </section>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                  <section className="p-6 bg-amber-50 rounded-2xl border border-amber-100">
                    <h4 className="font-bold text-amber-900 mb-3">Operational Gains: The 80/20 Rule</h4>
                    <p className="text-sm text-amber-800 leading-relaxed">
                      By automating the "Draft Zero" phase, we allow senior consultants to move away from the **80% volume tasks** (summarization, template filling, initial research) and focus exclusively on the **20% value tasks**: strategic advisory, multi-stakeholder negotiation, and final ethical oversight.
                    </p>
                  </section>
                  <section className="p-6 bg-blue-50 rounded-2xl border border-blue-100">
                    <h4 className="font-bold text-blue-900 mb-3">Future Evolution</h4>
                    <p className="text-sm text-blue-800 leading-relaxed">
                      With the integration of **Gemini 1.5 Pro**, future iterations will include **Autonomous Policy Analysis** (comparing interventions against global trends) and **Human-in-the-Loop 2.0** for collaborative real-time drafting.
                    </p>
                  </section>
                </div>

                <div className="text-center pt-8 border-t border-slate-100">
                  <p className="text-slate-400 font-mono text-xs uppercase tracking-widest">
                    AI should handle the data, so humans can handle the strategy.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
