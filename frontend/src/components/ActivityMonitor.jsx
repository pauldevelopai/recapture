import { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Smartphone, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ActivityMonitor() {
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState('');
    const [logs, setLogs] = useState([]);
    const [simulatedContent, setSimulatedContent] = useState('');
    const [isScanning, setIsScanning] = useState(false);

    useEffect(() => {
        fetchProfiles();
    }, []);

    useEffect(() => {
        if (selectedProfile) {
            fetchLogs(selectedProfile);
            // Poll for updates
            const interval = setInterval(() => fetchLogs(selectedProfile), 3000);
            return () => clearInterval(interval);
        }
    }, [selectedProfile]);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/profiles');
            setProfiles(res.data);
            if (res.data.length > 0 && !selectedProfile) {
                setSelectedProfile(res.data[0].id);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const fetchLogs = async (profileId) => {
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/profiles/${profileId}/logs`);
            setLogs(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSimulateIngestion = async () => {
        if (!simulatedContent.trim() || !selectedProfile) return;

        setIsScanning(true);
        try {
            await axios.post('http://127.0.0.1:8000/api/scanner/ingest', {
                profile_id: selectedProfile,
                content: simulatedContent,
                source_url: "Simulated Device Input",
                timestamp: new Date().toISOString()
            });
            setSimulatedContent('');
            // Immediate fetch to show pending state if we had one, but we rely on polling for analysis completion
            fetchLogs(selectedProfile);
        } catch (err) {
            console.error(err);
        } finally {
            setIsScanning(false);
        }
    };

    return (
        <div className="activity-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1>Activity Monitor</h1>
                    <p className="text-muted">Real-time scanning of content consumption.</p>
                </div>

                <select
                    value={selectedProfile}
                    onChange={(e) => setSelectedProfile(e.target.value)}
                    style={{ padding: '0.75rem', borderRadius: 'var(--radius)', minWidth: '200px' }}
                >
                    {profiles.map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
                <div className="card">
                    <h3><Clock size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Time Spent</h3>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)', margin: '1rem 0' }}>
                        {stats.total_time_spent_minutes} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>min</span>
                    </div>
                    <p className="text-muted">Total time across all platforms today.</p>
                </div>

                <div className="card">
                    <h3><AlertTriangle size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Risk Score</h3>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: stats.average_risk_score > 0.5 ? 'var(--danger)' : 'var(--success)', margin: '1rem 0' }}>
                        {(stats.average_risk_score * 10).toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 10</span>
                    </div>
                    <p className="text-muted">Average risk level of consumed content.</p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
                {/* Main Feed */}
                <div>
                    <div className="card">
                        <h3>Recent Activity Log</h3>
                        <div className="list">
                            {logs.map(log => (
                                <div key={log.id} style={{
                                    padding: '1rem',
                                    borderBottom: '1px solid var(--border)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    flexWrap: 'wrap',
                                    gap: '1rem'
                                }}>
                                    <div>
                                        <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>{log.platform}</div>
                                        <div className="text-muted" style={{ fontSize: '0.9rem' }}>{new Date(log.timestamp).toLocaleString()}</div>
                                    </div>
                                    <div style={{
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '1rem',
                                        background: log.risk_score > 0.5 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                                        color: log.risk_score > 0.5 ? 'var(--danger)' : 'var(--success)',
                                        fontSize: '0.9rem',
                                        fontWeight: 'bold'
                                    }}>
                                        Risk: {(log.risk_score * 10).toFixed(1)}
                                    </div>
                                </div>
                            ))}
                            {logs.length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '1rem' }}>No activity recorded yet.</p>}
                        </div>
                    </div>
                </div>

                {/* Simulation Sidebar */}
                <div>
                    <div className="card" style={{ position: 'sticky', top: '1rem' }}>
                        <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: 0 }}>
                            <Smartphone size={20} /> Simulator
                        </h3>
                        <p className="text-muted" style={{ fontSize: '0.875rem' }}>
                            Simulate incoming content from the child's device.
                        </p>

                        <textarea
                            value={simulatedContent}
                            onChange={(e) => setSimulatedContent(e.target.value)}
                            placeholder="Paste text content here..."
                            rows={5}
                            style={{ marginBottom: '1rem' }}
                        />

                        <button
                            onClick={handleSimulateIngestion}
                            disabled={isScanning || !simulatedContent.trim()}
                            style={{ width: '100%' }}
                        >
                            {isScanning ? 'Scanning...' : 'Ingest Content'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
