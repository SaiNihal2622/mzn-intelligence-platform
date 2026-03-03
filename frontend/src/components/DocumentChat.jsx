import { useState, useRef, useEffect } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function DocumentChat() {
    const [phase, setPhase] = useState('upload'); // 'upload' | 'chat'
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [docInfo, setDocInfo] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isSending, setIsSending] = useState(false);
    const [uploadError, setUploadError] = useState(null);
    const [expandedSources, setExpandedSources] = useState({});

    const fileInputRef = useRef(null);
    const chatBottomRef = useRef(null);

    useEffect(() => {
        chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleFile = async (file) => {
        if (!file) return;
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'txt', 'md'].includes(ext)) {
            setUploadError('Please upload a PDF, TXT, or MD file.');
            return;
        }
        setUploadError(null);
        setIsUploading(true);

        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await fetch(`${API_BASE}/upload-document`, { method: 'POST', body: formData });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Upload failed');
            }
            const data = await res.json();
            setDocInfo(data);
            setPhase('chat');
            setMessages([{
                role: 'assistant',
                content: `📄 I've read **${data.filename}** (${data.chunk_count} sections indexed).\n\nHere's a preview of what I found:\n> *"${data.preview}..."*\n\nAsk me anything about this document!`,
                sources: [],
            }]);
        } catch (err) {
            setUploadError(err.message);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFile(e.dataTransfer.files[0]);
    };

    const sendMessage = async (msg) => {
        const text = msg || inputValue.trim();
        if (!text || !docInfo?.doc_id) return;
        setInputValue('');

        const userMessage = { role: 'user', content: text, sources: [] };
        setMessages(prev => [...prev, userMessage]);
        setIsSending(true);

        try {
            const res = await fetch(`${API_BASE}/chat-document`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: docInfo.doc_id, message: text }),
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Chat failed');
            }
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources || [] }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: `❌ Error: ${err.message}`, sources: [] }]);
        } finally {
            setIsSending(false);
        }
    };

    const toggleSources = (idx) => setExpandedSources(prev => ({ ...prev, [idx]: !prev[idx] }));
    const resetChat = () => { setPhase('upload'); setDocInfo(null); setMessages([]); setUploadError(null); };

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            {phase === 'upload' ? (
                <div className="glass-panel" style={{ padding: '2.5rem' }}>
                    <h2 className="text-2xl font-bold mb-2 text-slate-800" style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '1rem' }}>
                        💬 Document Intelligence Chat
                    </h2>
                    <p className="text-slate-500 mb-8 text-sm leading-relaxed">
                        Upload any project report, RFP, policy brief, or donor framework. Then ask questions about it — our AI will answer using only what's in the document.
                    </p>

                    {/* Drop Zone */}
                    <div
                        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                        onDragLeave={() => setIsDragging(false)}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        style={{
                            border: `2px dashed ${isDragging ? '#3b82f6' : '#cbd5e1'}`,
                            borderRadius: '1rem',
                            padding: '3rem 2rem',
                            textAlign: 'center',
                            cursor: 'pointer',
                            background: isDragging ? 'rgba(59,130,246,0.05)' : 'rgba(248,250,252,0.8)',
                            transition: 'all 0.2s ease',
                        }}
                    >
                        <input ref={fileInputRef} type="file" accept=".pdf,.txt,.md" style={{ display: 'none' }} onChange={(e) => handleFile(e.target.files[0])} />
                        {isUploading ? (
                            <div>
                                <div className="spinner" style={{ width: '2.5rem', height: '2.5rem', margin: '0 auto 1rem', border: '3px solid #e2e8f0', borderTop: '3px solid #3b82f6', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                                <p className="text-slate-600 font-medium">Parsing and indexing your document...</p>
                            </div>
                        ) : (
                            <>
                                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📄</div>
                                <p className="font-semibold text-slate-700 mb-1">
                                    {isDragging ? 'Drop your document here!' : 'Drag & drop your document here'}
                                </p>
                                <p className="text-sm text-slate-400">or click to browse — PDF, TXT, or MD (max 20MB)</p>
                            </>
                        )}
                    </div>

                    {uploadError && (
                        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.5rem', padding: '0.75rem 1rem', marginTop: '1rem', color: '#991b1b', fontSize: '0.875rem' }}>
                            ⚠️ {uploadError}
                        </div>
                    )}

                    {/* Example use cases */}
                    <div style={{ marginTop: '2rem' }}>
                        <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">What you can chat with</p>
                        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                            {['📋 RFP Documents', '📊 Project Reports', '🌍 Policy Briefs', '💰 Donor Frameworks', '📁 Research Papers'].map(t => (
                                <span key={t} style={{ background: '#f1f5f9', borderRadius: '2rem', padding: '0.35rem 0.85rem', fontSize: '0.8rem', color: '#475569', border: '1px solid #e2e8f0' }}>{t}</span>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', height: '80vh', gap: '0' }}>
                    {/* Chat header */}
                    <div className="glass-panel" style={{ padding: '1rem 1.5rem', borderRadius: '1rem 1rem 0 0', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div>
                            <h3 className="font-bold text-slate-800" style={{ fontSize: '1rem' }}>📄 {docInfo?.filename}</h3>
                            <p className="text-xs text-slate-400">{docInfo?.chunk_count} sections indexed • Ask anything</p>
                        </div>
                        <button onClick={resetChat} style={{ fontSize: '0.75rem', color: '#64748b', background: '#f1f5f9', border: '1px solid #e2e8f0', borderRadius: '0.5rem', padding: '0.4rem 0.8rem', cursor: 'pointer' }}>
                            ↩ New Document
                        </button>
                    </div>

                    {/* Messages */}
                    <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', background: '#f8fafc', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                        {messages.map((msg, idx) => (
                            <div key={idx} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                                <div style={{
                                    maxWidth: '75%',
                                    background: msg.role === 'user' ? 'linear-gradient(135deg, #3b82f6, #2563eb)' : 'white',
                                    color: msg.role === 'user' ? 'white' : '#1e293b',
                                    borderRadius: msg.role === 'user' ? '1.25rem 1.25rem 0.25rem 1.25rem' : '1.25rem 1.25rem 1.25rem 0.25rem',
                                    padding: '0.875rem 1rem',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                                    border: msg.role === 'assistant' ? '1px solid #e2e8f0' : 'none',
                                }}>
                                    <p style={{ fontSize: '0.9rem', lineHeight: '1.6', whiteSpace: 'pre-wrap', margin: 0 }}>{msg.content}</p>
                                    {msg.role === 'assistant' && msg.sources?.length > 0 && (
                                        <div style={{ marginTop: '0.75rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.5rem' }}>
                                            <button onClick={() => toggleSources(idx)} style={{ fontSize: '0.7rem', color: '#64748b', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                                                {expandedSources[idx] ? '▲ Hide' : '▼ Show'} document sources ({msg.sources.length})
                                            </button>
                                            {expandedSources[idx] && msg.sources.map((s, si) => (
                                                <div key={si} style={{ background: '#f8fafc', borderRadius: '0.5rem', padding: '0.5rem 0.75rem', marginTop: '0.5rem', fontSize: '0.75rem', color: '#475569', borderLeft: '3px solid #3b82f6', lineHeight: 1.5 }}>
                                                    {s}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isSending && (
                            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                                <div style={{ background: 'white', borderRadius: '1.25rem', padding: '0.875rem 1.25rem', border: '1px solid #e2e8f0', boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
                                    <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                                        {[0, 0.15, 0.3].map((d, i) => (
                                            <div key={i} style={{ width: 7, height: 7, background: '#3b82f6', borderRadius: '50%', animation: `bounce 1s ease-in-out ${d}s infinite` }} />
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={chatBottomRef} />
                    </div>

                    {/* Suggested questions (shown only when first message) */}
                    {messages.length <= 1 && docInfo?.suggested_questions && (
                        <div style={{ padding: '0 1.5rem', background: '#f8fafc', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {docInfo.suggested_questions.map((q, i) => (
                                <button key={i} onClick={() => sendMessage(q)} style={{ fontSize: '0.75rem', background: 'white', border: '1px solid #e2e8f0', borderRadius: '2rem', padding: '0.4rem 0.9rem', color: '#3b82f6', cursor: 'pointer', boxShadow: '0 1px 4px rgba(0,0,0,0.06)' }}>
                                    {q}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <div style={{ padding: '1rem 1.5rem', background: 'white', borderTop: '1px solid #e2e8f0', borderRadius: '0 0 1rem 1rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
                        <textarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                            placeholder="Ask a question about the document... (Enter to send, Shift+Enter for new line)"
                            rows={2}
                            style={{
                                flex: 1, resize: 'none', border: '1.5px solid #e2e8f0', borderRadius: '0.75rem', padding: '0.75rem 1rem',
                                fontSize: '0.9rem', outline: 'none', fontFamily: 'inherit', transition: 'border-color 0.2s',
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
                            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                            disabled={isSending}
                        />
                        <button
                            onClick={() => sendMessage()}
                            disabled={isSending || !inputValue.trim()}
                            style={{
                                background: 'linear-gradient(135deg, #3b82f6, #2563eb)', color: 'white', border: 'none', borderRadius: '0.75rem',
                                padding: '0.75rem 1.25rem', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem',
                                opacity: isSending || !inputValue.trim() ? 0.5 : 1, transition: 'opacity 0.2s',
                            }}
                        >
                            Send →
                        </button>
                    </div>
                </div>
            )}

            <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
      `}</style>
        </div>
    );
}
