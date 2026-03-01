import { useState } from 'react';
import { Target, Layers, FileSignature, CheckSquare, ShieldAlert, FileText, CheckCircle2, ChevronRight, DollarSign, Calendar, Users } from 'lucide-react';

export default function ResultsDashboard({ results }) {
    const [activeTab, setActiveTab] = useState('funding');

    if (!results) return null;

    const tabs = [
        { id: 'funding', label: 'Funding', icon: DollarSign },
        { id: 'knowledge', label: 'Knowledge', icon: FileText },
        { id: 'proposal', label: 'Proposal', icon: FileSignature },
        { id: 'briefing', label: 'Briefing', icon: Users },
        { id: 'workflow', label: 'Tasks', icon: CheckSquare },
        { id: 'compliance', label: 'Compliance', icon: ShieldAlert },
    ];

    return (
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="glass-header">
                <h2 className="text-lg font-semibold" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers style={{ color: 'var(--accent-blue)', width: '20px', height: '20px' }} />
                    Intelligence Analysis Results
                </h2>
                <span className="badge badge-success">
                    <CheckCircle2 style={{ width: '14px', height: '14px' }} />
                    Pipeline Complete ({results.metadata?.pipeline_duration_seconds}s)
                </span>
            </div>

            <div style={{ background: 'var(--bg-card)', borderBottom: '1px solid var(--border-color)' }}>
                <nav className="tabs-nav">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        >
                            <tab.icon style={{ width: '16px', height: '16px' }} />
                            {tab.label}
                        </button>
                    ))}
                </nav>
            </div>

            <div className="results-content">
                {/* Funding Matches */}
                {activeTab === 'funding' && (
                    <section>
                        <div className="grid-2">
                            {results.funding_matches?.map((match, idx) => (
                                <div key={idx} className="card-item">
                                    <div className="card-header">
                                        <h4 className="card-title">{match.donor_name}</h4>
                                        <span className="badge badge-success">
                                            Score: {match.relevance_score.toFixed(2)}
                                        </span>
                                    </div>
                                    <p className="text-sm text-muted mb-4" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                        {match.description}
                                    </p>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Target style={{ width: '14px', height: '14px' }} /> {match.sector}</div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Users style={{ width: '14px', height: '14px' }} /> {match.eligibility}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {(!results.funding_matches || results.funding_matches.length === 0) && (
                            <p className="text-sm text-muted" style={{ fontStyle: 'italic', marginTop: '1rem' }}>No funding opportunities matched explicitly.</p>
                        )}
                    </section>
                )}

                {/* Similar Projects */}
                {activeTab === 'knowledge' && (
                    <section className="space-y-4">
                        {results.similar_projects?.map((proj, idx) => (
                            <div key={idx} className="card-item" style={{ display: 'flex', gap: '1rem', background: 'rgba(248, 250, 252, 0.7)' }}>
                                <div style={{ flexShrink: 0 }}>
                                    <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(99, 102, 241, 0.1)', color: '#4f46e5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '0.75rem' }}>
                                        {idx + 1}
                                    </div>
                                </div>
                                <div>
                                    <h4 className="card-title mb-1">{proj.source}</h4>
                                    <p className="text-sm text-muted">"{proj.text}"</p>
                                </div>
                            </div>
                        ))}
                    </section>
                )}

                {/* Proposal Outline */}
                {activeTab === 'proposal' && (
                    <section>
                        <div className="card-item" style={{ padding: 0, overflow: 'hidden' }}>
                            <div className="glass-header" style={{ borderBottom: '1px solid var(--border-color)', borderRadius: 0 }}>
                                <h4 className="card-title text-lg">{results.proposal_outline?.title}</h4>
                            </div>
                            <div style={{ padding: '1.5rem' }} className="space-y-4 text-sm">
                                <div>
                                    <strong style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                                        <ChevronRight style={{ width: '16px', height: '16px', color: '#a855f7' }} /> Problem Statement:
                                    </strong>
                                    <p className="text-muted" style={{ margin: '4px 0 0 24px' }}>{results.proposal_outline?.problem}</p>
                                </div>
                                <div>
                                    <strong style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                                        <ChevronRight style={{ width: '16px', height: '16px', color: '#a855f7' }} /> Solution Approach:
                                    </strong>
                                    <p className="text-muted" style={{ margin: '4px 0 0 24px' }}>{results.proposal_outline?.solution}</p>
                                </div>
                                <div>
                                    <strong style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-primary)' }}>
                                        <ChevronRight style={{ width: '16px', height: '16px', color: '#a855f7' }} /> Expected Impact:
                                    </strong>
                                    <ul className="text-muted" style={{ margin: '4px 0 0 40px', listStyleType: 'disc' }}>
                                        {results.proposal_outline?.impact?.map((imp, i) => <li key={i} style={{ marginBottom: '4px' }}>{imp}</li>)}
                                    </ul>
                                </div>
                                <div style={{ paddingTop: '1rem', marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', fontWeight: 500, display: 'flex', justifyContent: 'space-between' }}>
                                    <span className="text-muted">Suggested Budget: {results.proposal_outline?.budget_concept?.total_estimated}</span>
                                    <span style={{ color: '#9333ea', cursor: 'pointer' }}>{results.proposal_outline?.budget_concept?.notes}</span>
                                </div>
                            </div>
                        </div>
                    </section>
                )}

                {/* Consultant Briefing */}
                {activeTab === 'briefing' && (
                    <section>
                        <div className="card-item" style={{ background: 'rgba(239, 246, 255, 0.5)', borderColor: '#bfdbfe' }}>
                            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.875rem', color: '#334155', lineHeight: 1.6, fontWeight: 500 }}>
                                {results.consultant_briefing}
                            </pre>
                        </div>
                    </section>
                )}

                {/* Workflow Tasks */}
                {activeTab === 'workflow' && (
                    <section className="space-y-4">
                        {results.workflow_tasks?.map((task, idx) => (
                            <div key={idx} className="card-item" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 1rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <div style={{
                                        width: '8px', height: '8px', borderRadius: '50%',
                                        background: task.priority === 'critical' ? '#ef4444' : task.priority === 'high' ? '#f97316' : '#3b82f6'
                                    }} />
                                    <div>
                                        <h4 className="card-title text-sm">{task.title}</h4>
                                        <p className="text-xs text-muted">Assignee: {task.owner} | {task.sprint}</p>
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 500, background: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0' }}>
                                        <Calendar style={{ width: '12px', height: '12px' }} /> {task.estimated_hours}h
                                    </span>
                                </div>
                            </div>
                        ))}
                    </section>
                )}

                {/* Compliance */}
                {activeTab === 'compliance' && (
                    <section>
                        <div className="card-item" style={{ background: '#fef2f2', borderColor: '#fecaca', display: 'flex', gap: '12px' }}>
                            <ShieldAlert style={{ width: '24px', height: '24px', color: '#dc2626', flexShrink: 0 }} />
                            <div>
                                <h3 style={{ fontWeight: 600, color: '#991b1b', marginBottom: '8px' }}>GDPR & Responsible AI Notice</h3>
                                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: '0.875rem', color: '#7f1d1d', lineHeight: 1.6, opacity: 0.9 }}>
                                    {results.compliance_notes}
                                </pre>
                            </div>
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}
