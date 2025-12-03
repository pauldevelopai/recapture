import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, Activity, Shield, Users } from 'lucide-react';

export default function Dashboard() {
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState('');
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfiles();
    }, []);

    useEffect(() => {
        if (selectedProfile) {
            fetchLogs(selectedProfile);
        } else {
            setLogs([]);
        }
    }, [selectedProfile]);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/subjects');
            setProfiles(res.data);
            if (res.data.length > 0) setSelectedProfile(res.data[0].id);
        } catch (e) { console.error("Failed to fetch profiles", e); }
    };

    const fetchLogs = async (pid) => {
        setLoading(true);
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/subjects/${pid}/logs`);
            setLogs(res.data);
        } catch (e) { console.error("Failed to fetch logs", e); }
        finally { setLoading(false); }
    };

    // Calculate Stats
    const totalScans = logs.length;
    const avgRisk = logs.length > 0 ? logs.reduce((acc, l) => acc + (l.risk_score || 0), 0) / logs.length : 0;

    // Determine Risk Level Label
    let riskLabel = "Low";
    let riskColor = "var(--success)";
    let riskBg = "rgba(34, 197, 94, 0.1)";

    if (avgRisk > 0.7) {
        riskLabel = "High";
        riskColor = "var(--danger)";
        riskBg = "rgba(239, 68, 68, 0.1)";
    } else if (avgRisk > 0.3) {
        riskLabel = "Moderate";
        riskColor = "var(--warning)";
        riskBg = "rgba(234, 179, 8, 0.1)";
    }

    // Mock Progress (since we don't have historical snapshots yet)
    // In a real app, we'd compare this week vs last week.
    const progress = logs.length > 5 ? "+15%" : "0%";

    return (
        <div className="dashboard">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1>Success Tracking</h1>
                    <p className="text-muted">Track the progress of recapturing and de-radicalization efforts.</p>
                </div>

                <div style={{ position: 'relative' }}>
                    <Users size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <select
                        value={selectedProfile}
                        onChange={(e) => setSelectedProfile(e.target.value)}
                        style={{ padding: '0.5rem 0.5rem 0.5rem 2.5rem', borderRadius: 'var(--radius)', minWidth: '200px' }}
                    >
                        {profiles.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        {profiles.length === 0 && <option value="">No profiles found</option>}
                    </select>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <div className="card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '50%', color: 'var(--primary)' }}>
                            <Activity size={24} />
                        </div>
                        <div>
                            <div className="text-muted" style={{ fontSize: '0.875rem' }}>Total Scans</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{totalScans}</div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <div style={{ padding: '0.75rem', background: riskBg, borderRadius: '50%', color: riskColor }}>
                            <Shield size={24} />
                        </div>
                        <div>
                            <div className="text-muted" style={{ fontSize: '0.875rem' }}>Avg Risk Level</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700', color: riskColor }}>{riskLabel}</div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                        <div style={{ padding: '0.75rem', background: 'rgba(34, 197, 94, 0.1)', borderRadius: '50%', color: 'var(--success)' }}>
                            <TrendingUp size={24} />
                        </div>
                        <div>
                            <div className="text-muted" style={{ fontSize: '0.875rem' }}>Progress</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{progress}</div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="card">
                <h3>Recent Activity Log</h3>
                {loading ? <p>Loading activity...</p> : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {logs.slice(0, 5).map((log) => (
                            <div key={log.id} style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                padding: '1rem',
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: 'var(--radius)',
                                flexWrap: 'wrap',
                                gap: '0.5rem'
                            }}>
                                <div>
                                    <div style={{ fontWeight: '500' }}>Content Scan</div>
                                    <div className="text-muted" style={{ fontSize: '0.875rem' }}>
                                        {log.content.substring(0, 50)}...
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div className="text-muted" style={{ fontSize: '0.875rem' }}>{new Date(log.timestamp).toLocaleString()}</div>
                                    <div style={{
                                        fontSize: '0.8rem',
                                        color: (log.risk_score || 0) > 0.5 ? 'var(--danger)' : 'var(--success)',
                                        fontWeight: 'bold'
                                    }}>
                                        Risk: {((log.risk_score || 0) * 10).toFixed(1)}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {logs.length === 0 && <p className="text-muted">No activity recorded for this profile.</p>}
                    </div>
                )}
            </div>
        </div>
    );
}
