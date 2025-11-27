import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Bot, User, RefreshCw, MessageSquare, Plus, AlertTriangle } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

export default function CloneDashboard() {
    const navigate = useNavigate();
    const [subjects, setSubjects] = useState([]);
    const [clones, setClones] = useState({});
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [subjectsRes, clonesRes] = await Promise.all([
                axios.get(`${API_URL}/subjects`),
                axios.get(`${API_URL}/clones`)
            ]);

            setSubjects(subjectsRes.data);

            // Map clones by subject_id for easy lookup
            const cloneMap = {};
            clonesRes.data.forEach(clone => {
                cloneMap[clone.subject_id] = clone;
            });
            setClones(cloneMap);

        } catch (err) {
            console.error("Error fetching dashboard data:", err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'ready': return 'var(--success)';
            case 'pending': return 'var(--warning)';
            default: return 'var(--text-muted)';
        }
    };

    return (
        <div className="clone-dashboard">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1>Digital Clone Lab</h1>
                    <p className="text-muted">Create and interact with digital simulations of subjects to test arguments.</p>
                </div>
                <button onClick={fetchData} style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                    <RefreshCw size={18} style={{ marginRight: '0.5rem' }} /> Refresh
                </button>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <RefreshCw size={32} className="spin" style={{ marginBottom: '1rem', animation: 'spin 1s linear infinite' }} />
                    <p>Loading Clone Lab...</p>
                    <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
                    {subjects.map(subject => {
                        const clone = clones[subject.id];
                        return (
                            <div key={subject.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}>
                                            {clone ? <Bot size={24} color="var(--accent)" /> : <User size={24} />}
                                        </div>
                                        <div>
                                            <h3 style={{ margin: 0 }}>{subject.name}</h3>
                                            <span className="text-muted">{subject.age} years old</span>
                                        </div>
                                    </div>
                                    {clone && (
                                        <span style={{
                                            padding: '0.25rem 0.75rem',
                                            borderRadius: '1rem',
                                            fontSize: '0.75rem',
                                            background: `rgba(${clone.status === 'ready' ? '34, 197, 94' : '251, 191, 36'}, 0.2)`,
                                            color: getStatusColor(clone.status),
                                            textTransform: 'uppercase',
                                            fontWeight: 'bold'
                                        }}>
                                            {clone.status}
                                        </span>
                                    )}
                                </div>

                                <div style={{ flex: 1, marginBottom: '1.5rem' }}>
                                    {clone ? (
                                        <div style={{ fontSize: '0.9rem', display: 'grid', gap: '0.5rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <span className="text-muted">Training Posts:</span>
                                                <span>{clone.training_post_count}</span>
                                            </div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                <span className="text-muted">Last Trained:</span>
                                                <span>{clone.last_trained ? new Date(clone.last_trained).toLocaleDateString() : 'Never'}</span>
                                            </div>
                                            {clone.status === 'pending' && (
                                                <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(251, 191, 36, 0.1)', borderRadius: '0.5rem', fontSize: '0.8rem', color: 'var(--warning)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                                    <AlertTriangle size={14} />
                                                    Needs social media data to train.
                                                </div>
                                            )}
                                        </div>
                                    ) : (
                                        <p className="text-muted" style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>
                                            No digital clone created yet. Create one to start testing arguments.
                                        </p>
                                    )}
                                </div>

                                <div style={{ marginTop: 'auto' }}>
                                    {clone ? (
                                        <button
                                            onClick={() => navigate(`/subjects/${subject.id}/clone`)}
                                            style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                                        >
                                            <MessageSquare size={18} />
                                            {clone.status === 'ready' ? 'Launch Simulation' : 'Setup Clone'}
                                        </button>
                                    ) : (
                                        <button
                                            onClick={() => navigate(`/subjects/${subject.id}/clone`)}
                                            style={{ width: '100%', background: 'var(--surface)', border: '1px solid var(--primary)', color: 'var(--primary)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}
                                        >
                                            <Plus size={18} />
                                            Create Clone
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}

                    {subjects.length === 0 && (
                        <div className="card" style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem' }}>
                            <p className="text-muted">No subjects found. Add subjects first to create clones.</p>
                            <button onClick={() => navigate('/')}>Go to Subjects</button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
