import { useState, useEffect } from 'react';
import { MessageSquare, Copy, Check, User } from 'lucide-react';
import axios from 'axios';

export default function ArgumentBuilder() {
    const [context, setContext] = useState('');
    const [profiles, setProfiles] = useState([]);
    const [selectedProfileId, setSelectedProfileId] = useState('');
    const [authorities, setAuthorities] = useState([]);
    const [generatedArgument, setGeneratedArgument] = useState(null);
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        fetchProfiles();
    }, []);

    useEffect(() => {
        if (selectedProfileId) {
            fetchAuthorities(selectedProfileId);
        } else {
            setAuthorities([]);
        }
    }, [selectedProfileId]);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/subjects');
            setProfiles(res.data);
        } catch (err) {
            console.error("Error fetching profiles:", err);
        }
    };

    const fetchAuthorities = async (subjectId) => {
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/subjects/${subjectId}/authorities`);
            setAuthorities(res.data);
        } catch (err) {
            console.error("Error fetching authorities:", err);
            setAuthorities([]);
        }
    };

    const handleGenerate = async () => {
        setLoading(true);
        try {
            const res = await axios.post('http://127.0.0.1:8000/api/generate-argument', {
                context: context,
                profile_id: selectedProfileId || null
            });
            setGeneratedArgument({
                text: res.data.argument_text,
                points: res.data.talking_points
            });
        } catch (err) {
            console.error("Error generating argument:", err);
            alert("Failed to generate argument. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (generatedArgument) {
            navigator.clipboard.writeText(generatedArgument.text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="argument-page">
            <h1>Argument Builder</h1>
            <p className="text-muted" style={{ marginBottom: '2rem' }}>
                Generate empathetic and effective counter-arguments based on radicalization analysis.
            </p>

            <div className="card">
                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Select Young Person (Optional)</label>
                    <div style={{ position: 'relative' }}>
                        <select
                            className="input"
                            value={selectedProfileId}
                            onChange={(e) => setSelectedProfileId(e.target.value)}
                            style={{ appearance: 'none', width: '100%' }}
                        >
                            <option value="">General / No Specific Profile</option>
                            {profiles.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                        <User size={16} style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                    </div>
                    <small className="text-muted">Selecting a profile tailors the tone to their age and risk level.</small>
                </div>

                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                    Context / Topic {selectedProfileId && <span className="text-muted" style={{ fontWeight: 'normal' }}>(Optional - will use profile history if empty)</span>}
                </label>
                <input
                    type="text"
                    className="input"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder={selectedProfileId ? "E.g., Specific incident (optional)..." : "E.g., Flat Earth theory, Anti-vax sentiments..."}
                    style={{ marginBottom: '1rem' }}
                />

                {selectedProfileId && (
                    <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: 'var(--radius)', marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--primary)' }}>
                        <strong><User size={14} style={{ verticalAlign: 'middle', marginRight: '0.25rem' }} /> Profile Context Active:</strong> The AI will use this person's risk level, recent history, and trusted authorities to tailor the argument.
                    </div>
                )}

                {selectedProfileId && authorities.length > 0 && (
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                            Trusted Authorities ({authorities.length})
                        </label>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {authorities.map((auth) => (
                                <div key={auth.id} style={{
                                    padding: '0.75rem',
                                    background: 'rgba(34, 197, 94, 0.1)',
                                    borderRadius: 'var(--radius)',
                                    border: '1px solid rgba(34, 197, 94, 0.3)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}>
                                    <div>
                                        <div style={{ fontWeight: 'bold', color: 'var(--success)' }}>{auth.name}</div>
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                                            {auth.role} • {auth.relation}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <small className="text-muted" style={{ display: 'block', marginTop: '0.5rem' }}>
                            These authorities will be referenced in the generated argument to build trust.
                        </small>
                    </div>
                )}

                <button
                    className="btn btn-primary"
                    onClick={handleGenerate}
                    disabled={loading || (!context.trim() && !selectedProfileId)}
                    style={{ width: '100%' }}
                >
                    {loading ? 'Generating...' : 'Generate Argument'}
                </button>
            </div>

            {generatedArgument && (
                <div className="card" style={{ borderColor: 'var(--primary)', marginTop: '2rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                        <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <MessageSquare size={20} /> Suggested Script
                        </h3>
                        <button
                            onClick={copyToClipboard}
                            style={{
                                padding: '0.5rem',
                                background: 'transparent',
                                border: 'none',
                                color: copied ? 'var(--success)' : 'var(--text-muted)',
                                cursor: 'pointer'
                            }}
                            title="Copy to clipboard"
                        >
                            {copied ? <Check size={20} /> : <Copy size={20} />}
                        </button>
                    </div>

                    <div style={{
                        background: 'rgba(0,0,0,0.2)',
                        padding: '1rem',
                        borderRadius: 'var(--radius)',
                        marginBottom: '1.5rem',
                        whiteSpace: 'pre-wrap',
                        lineHeight: '1.6'
                    }}>
                        {generatedArgument.text}
                    </div>

                    <div>
                        <strong>Key Talking Points:</strong>
                        <ul style={{ color: 'var(--text-muted)', marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                            {generatedArgument.points.map((point, i) => (
                                <li key={i} style={{ marginBottom: '0.5rem' }}>{point}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
