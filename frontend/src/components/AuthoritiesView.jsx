import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserCheck, Plus, Trash2, Users, AlertTriangle, Shield, Check, ArrowRight } from 'lucide-react';

export default function AuthoritiesView() {
    const [subjects, setSubjects] = useState([]);
    const [atRiskSubjects, setAtRiskSubjects] = useState([]);
    const [selectedSubject, setSelectedSubject] = useState('');
    const [authorities, setAuthorities] = useState([]);
    const [recommendations, setRecommendations] = useState(null);
    const [newAuthority, setNewAuthority] = useState({ name: '', role: '', relation: '' });
    const [isAdding, setIsAdding] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchSubjects();
        fetchAtRiskSubjects();
    }, []);

    useEffect(() => {
        if (selectedSubject) {
            fetchAuthorities(selectedSubject);
            fetchRecommendations(selectedSubject);
        } else {
            setAuthorities([]);
            setRecommendations(null);
        }
    }, [selectedSubject]);

    const fetchSubjects = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/subjects');
            setSubjects(res.data);
            if (res.data.length > 0 && !selectedSubject) setSelectedSubject(res.data[0].id);
        } catch (e) { console.error("Failed to fetch subjects", e); }
    };

    const fetchAtRiskSubjects = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/subjects/at-risk');
            setAtRiskSubjects(res.data);
        } catch (e) { console.error("Failed to fetch at-risk subjects", e); }
    };

    const fetchAuthorities = async (sid) => {
        setLoading(true);
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/subjects/${sid}/authorities`);
            setAuthorities(res.data);
        } catch (e) { console.error("Failed to fetch authorities", e); }
        finally { setLoading(false); }
    };

    const fetchRecommendations = async (sid) => {
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/subjects/${sid}/recommended-authorities`);
            setRecommendations(res.data);
        } catch (e) { console.error("Failed to fetch recommendations", e); }
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newAuthority.name || !selectedSubject) return;

        try {
            await axios.post(`http://127.0.0.1:8000/api/subjects/${selectedSubject}/authorities`, {
                ...newAuthority,
                subject_id: selectedSubject
            });
            setNewAuthority({ name: '', role: '', relation: '' });
            setIsAdding(false);
            fetchAuthorities(selectedSubject);
        } catch (e) { alert("Failed to add authority"); }
    };

    const handleAssignRecommendation = async (rec) => {
        try {
            await axios.post(`http://127.0.0.1:8000/api/subjects/${selectedSubject}/authorities`, {
                name: rec.authority.name,
                role: rec.authority.role,
                relation: rec.authority.relation,
                subject_id: selectedSubject
            });
            fetchAuthorities(selectedSubject);
            alert(`Assigned ${rec.authority.name} to subject!`);
        } catch (e) { alert("Failed to assign authority"); }
    };

    const handleDelete = async (id) => {
        if (!selectedSubject) return;
        try {
            await axios.delete(`http://127.0.0.1:8000/api/subjects/${selectedSubject}/authorities/${id}`);
            fetchAuthorities(selectedSubject);
        } catch (e) { alert("Failed to delete authority"); }
    };

    return (
        <div className="authorities-view" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '2rem', alignItems: 'start' }}>

            {/* Sidebar: Subject Selection */}
            <div className="card" style={{ padding: '0' }}>
                <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)' }}>
                    <h3 style={{ margin: 0 }}>Subjects</h3>
                </div>

                {/* At Risk Section */}
                {atRiskSubjects.length > 0 && (
                    <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', background: 'rgba(239, 68, 68, 0.05)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--danger)', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 'bold' }}>
                            <AlertTriangle size={14} />
                            NEEDS INTERVENTION
                        </div>
                        <div style={{ display: 'grid', gap: '0.5rem' }}>
                            {atRiskSubjects.map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => setSelectedSubject(s.id)}
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: '0.75rem',
                                        background: selectedSubject === s.id ? 'var(--primary)' : 'var(--surface)',
                                        border: '1px solid var(--danger)',
                                        borderRadius: '6px',
                                        color: selectedSubject === s.id ? 'white' : 'var(--text)',
                                        cursor: 'pointer',
                                        textAlign: 'left',
                                        width: '100%'
                                    }}
                                >
                                    <span>{s.name}</span>
                                    <span style={{ fontSize: '0.75rem', background: 'var(--danger)', color: 'white', padding: '0.1rem 0.4rem', borderRadius: '1rem' }}>
                                        {s.analysis.current_risk_score}/10
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* All Subjects List */}
                <div style={{ padding: '1rem' }}>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>ALL SUBJECTS</div>
                    <div style={{ display: 'grid', gap: '0.5rem' }}>
                        {subjects.map(s => (
                            <button
                                key={s.id}
                                onClick={() => setSelectedSubject(s.id)}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.75rem',
                                    padding: '0.75rem',
                                    background: selectedSubject === s.id ? 'var(--primary)' : 'transparent',
                                    border: 'none',
                                    borderRadius: '6px',
                                    color: selectedSubject === s.id ? 'white' : 'var(--text)',
                                    cursor: 'pointer',
                                    textAlign: 'left',
                                    width: '100%'
                                }}
                            >
                                <Users size={16} />
                                {s.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div>
                        <h1>Authority Management</h1>
                        <p className="text-muted">
                            {subjects.find(s => s.id === selectedSubject)?.name ?
                                `Managing authorities for ${subjects.find(s => s.id === selectedSubject)?.name}` :
                                (
                                    <span style={{ display: 'block', marginTop: '1rem', padding: '2rem', border: '1px dashed var(--border)', borderRadius: '8px', textAlign: 'center' }}>
                                        <ArrowRight size={32} style={{ marginBottom: '1rem', color: 'var(--primary)' }} />
                                        <br />
                                        <strong>Select a subject from the sidebar</strong> to view AI-recommended authorities and manage interventions.
                                        <br />
                                        <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                            Subjects marked with <AlertTriangle size={12} style={{ display: 'inline', verticalAlign: 'middle' }} /> need immediate attention.
                                        </span>
                                    </span>
                                )}
                        </p>
                    </div>
                    <button className="btn btn-primary" onClick={() => setIsAdding(!isAdding)} disabled={!selectedSubject}>
                        <Plus size={18} />
                        Add Manually
                    </button>
                </div>

                {/* Recommendations Panel */}
                {recommendations && recommendations.recommendations.length > 0 && (
                    <div className="card" style={{ marginBottom: '2rem', border: '1px solid var(--primary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                            <Shield size={20} style={{ color: 'var(--primary)' }} />
                            <h3 style={{ margin: 0 }}>AI Recommendations</h3>
                        </div>
                        <p className="text-muted" style={{ marginBottom: '1rem' }}>
                            Based on detected themes: {recommendations.detected_themes.join(', ')}
                        </p>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
                            {recommendations.recommendations.map((rec, i) => {
                                const isAssigned = authorities.some(a => a.name === rec.authority.name);
                                return (
                                    <div key={i} style={{
                                        padding: '1rem',
                                        background: 'rgba(255,255,255,0.05)',
                                        borderRadius: '8px',
                                        border: '1px solid var(--border)'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                            <strong>{rec.authority.name}</strong>
                                            <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>{Math.round(rec.match_score * 100)}% Match</span>
                                        </div>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                            {rec.authority.role} • {rec.authority.relation}
                                        </div>
                                        {isAssigned ? (
                                            <button disabled className="btn" style={{ width: '100%', opacity: 0.5 }}>
                                                <Check size={16} style={{ marginRight: '0.5rem' }} /> Assigned
                                            </button>
                                        ) : (
                                            <button
                                                className="btn btn-primary"
                                                style={{ width: '100%' }}
                                                onClick={() => handleAssignRecommendation(rec)}
                                            >
                                                <Plus size={16} style={{ marginRight: '0.5rem' }} /> Assign
                                            </button>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Manual Add Form */}
                {isAdding && (
                    <div className="card" style={{ marginBottom: '2rem' }}>
                        <h3>Add New Authority</h3>
                        <form onSubmit={handleAdd} style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
                                <input
                                    type="text"
                                    className="input"
                                    value={newAuthority.name}
                                    onChange={e => setNewAuthority({ ...newAuthority, name: e.target.value })}
                                    placeholder="e.g. Father John"
                                />
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Role</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={newAuthority.role}
                                        onChange={e => setNewAuthority({ ...newAuthority, role: e.target.value })}
                                        placeholder="e.g. Priest"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem' }}>Relation</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={newAuthority.relation}
                                        onChange={e => setNewAuthority({ ...newAuthority, relation: e.target.value })}
                                        placeholder="e.g. Spiritual Advisor"
                                    />
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                                <button type="button" className="btn" onClick={() => setIsAdding(false)}>Cancel</button>
                                <button type="submit" className="btn btn-primary">Save Authority</button>
                            </div>
                        </form>
                    </div>
                )}

                {/* Active Authorities List */}
                <div style={{ display: 'grid', gap: '1rem' }}>
                    <h3 style={{ margin: 0 }}>Active Authorities</h3>
                    {loading ? <p>Loading authorities...</p> : authorities.map(auth => (
                        <div key={auth.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '50%', color: 'var(--primary)' }}>
                                    <UserCheck size={24} />
                                </div>
                                <div>
                                    <h3 style={{ margin: 0 }}>{auth.name}</h3>
                                    <div className="text-muted">{auth.role} • {auth.relation}</div>
                                </div>
                            </div>
                            <button
                                className="btn"
                                style={{ color: 'var(--danger)', padding: '0.5rem' }}
                                onClick={() => handleDelete(auth.id)}
                            >
                                <Trash2 size={18} />
                            </button>
                        </div>
                    ))}
                    {!loading && authorities.length === 0 && (
                        <div className="text-muted" style={{ textAlign: 'center', padding: '2rem', border: '1px dashed var(--border)', borderRadius: 'var(--radius)' }}>
                            No authorities assigned yet. Use recommendations or add manually.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
