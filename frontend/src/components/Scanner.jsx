import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, Loader, Upload, FileText, Link, User } from 'lucide-react';

export default function Scanner() {
    const [activeTab, setActiveTab] = useState('text');
    const [text, setText] = useState('');
    const [profiles, setProfiles] = useState([]);
    const [selectedProfileId, setSelectedProfileId] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProfiles();
    }, []);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/profiles');
            setProfiles(res.data);
        } catch (err) {
            console.error("Error fetching profiles:", err);
        }
    };

    const handleAnalyze = async () => {
        if (!text.trim() && activeTab === 'text') return;
        if (activeTab === 'file') {
            alert("File upload is a mock feature for now.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await axios.post('http://127.0.0.1:8000/analyze', {
                text,
                profile_id: selectedProfileId || null
            });
            setResult(response.data);
        } catch (err) {
            setError('Failed to analyze content. Please ensure the backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="scanner-page">
            <h1>Digital Diet Scanner</h1>
            <p className="text-muted" style={{ marginBottom: '2rem' }}>
                Scan the entire information diet of a young person to detect harmful patterns.
            </p>

            <div className="card">
                <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Select Young Person (Optional)</label>
                    <div style={{ position: 'relative' }}>
                        <select
                            className="input"
                            value={selectedProfileId}
                            onChange={(e) => setSelectedProfileId(e.target.value)}
                            style={{ appearance: 'none', width: '100%' }}
                        >
                            <option value="">General Scan (No Profile)</option>
                            {profiles.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                        <User size={16} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                    </div>
                    <small className="text-muted">Linking a scan to a profile logs it to their history.</small>
                </div>

                <div className="tabs" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                    <button
                        className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
                        onClick={() => setActiveTab('text')}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'none',
                            border: 'none',
                            borderBottom: activeTab === 'text' ? '2px solid var(--primary)' : 'none',
                            color: activeTab === 'text' ? 'white' : 'var(--text-muted)',
                            cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: '0.5rem'
                        }}
                    >
                        <FileText size={16} /> Text / URL
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'file' ? 'active' : ''}`}
                        onClick={() => setActiveTab('file')}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'none',
                            border: 'none',
                            borderBottom: activeTab === 'file' ? '2px solid var(--primary)' : 'none',
                            color: activeTab === 'file' ? 'white' : 'var(--text-muted)',
                            cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: '0.5rem'
                        }}
                    >
                        <Upload size={16} /> File Upload
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'social' ? 'active' : ''}`}
                        onClick={() => setActiveTab('social')}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'none',
                            border: 'none',
                            borderBottom: activeTab === 'social' ? '2px solid var(--primary)' : 'none',
                            color: activeTab === 'social' ? 'white' : 'var(--text-muted)',
                            cursor: 'pointer',
                            display: 'flex', alignItems: 'center', gap: '0.5rem'
                        }}
                    >
                        <Link size={16} /> Social Media Dump
                    </button>
                </div>

                {activeTab === 'text' && (
                    <textarea
                        className="input"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste content, comments, or URLs here..."
                        rows={6}
                        style={{ marginBottom: '1rem', width: '100%' }}
                    />
                )}

                {activeTab === 'file' && (
                    <div style={{
                        border: '2px dashed var(--border)',
                        borderRadius: 'var(--radius)',
                        padding: '2rem',
                        textAlign: 'center',
                        marginBottom: '1rem',
                        color: 'var(--text-muted)'
                    }}>
                        <Upload size={32} style={{ marginBottom: '1rem' }} />
                        <p>Drag and drop files here (PDF, TXT, JSON)</p>
                        <small>Supports chat logs, browser history exports, etc.</small>
                    </div>
                )}

                {activeTab === 'social' && (
                    <div style={{
                        border: '2px dashed var(--border)',
                        borderRadius: 'var(--radius)',
                        padding: '2rem',
                        textAlign: 'center',
                        marginBottom: '1rem',
                        color: 'var(--text-muted)'
                    }}>
                        <Link size={32} style={{ marginBottom: '1rem' }} />
                        <p>Connect Social Media Account (Mock)</p>
                        <small>Analyze feed and interactions directly.</small>
                    </div>
                )}

                <button
                    className="btn btn-primary"
                    onClick={handleAnalyze}
                    disabled={loading || (activeTab === 'text' && !text.trim())}
                    style={{ width: '100%' }}
                >
                    {loading ? (
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                            <Loader className="animate-spin" size={18} /> Scanning...
                        </span>
                    ) : (
                        'Scan Information Diet'
                    )}
                </button>
            </div>

            {error && (
                <div className="card" style={{ borderColor: 'var(--danger)', color: 'var(--danger)', marginTop: '1rem' }}>
                    <AlertTriangle size={20} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                    {error}
                </div>
            )}

            {result && (
                <div className="card" style={{ borderColor: result.radicalization_score > 0.5 ? 'var(--danger)' : 'var(--success)', marginTop: '2rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                        {result.radicalization_score > 0.5 ? (
                            <AlertTriangle size={32} color="var(--danger)" />
                        ) : (
                            <CheckCircle size={32} color="var(--success)" />
                        )}
                        <div>
                            <h3 style={{ margin: 0 }}>Analysis Complete</h3>
                            <span style={{ color: 'var(--text-muted)' }}>
                                Risk Score: {(result.radicalization_score * 100).toFixed(0)}%
                            </span>
                        </div>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <strong>Detected Themes:</strong>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                            {result.detected_themes.map((theme, i) => (
                                <span key={i} style={{
                                    background: 'rgba(255,255,255,0.1)',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '1rem',
                                    fontSize: '0.875rem'
                                }}>
                                    {theme}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div>
                        <strong>Summary:</strong>
                        <p style={{ marginTop: '0.5rem', color: 'var(--text-muted)' }}>{result.summary}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
