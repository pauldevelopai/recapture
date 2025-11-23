import { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, ShieldAlert, ExternalLink } from 'lucide-react';

export default function ThreatMonitor() {
    const [trends, setTrends] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchTrends = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/trends');
                setTrends(response.data);
            } catch (error) {
                console.error("Failed to fetch trends", error);
            } finally {
                setLoading(false);
            }
        };

        fetchTrends();
    }, []);

    return (
        <div className="threat-monitor">
            <h1 style={{ marginBottom: '2rem' }}>Threat Monitor</h1>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
                {trends.map(trend => (
                    <div key={trend.id} className="card" style={{ borderTop: `4px solid ${trend.risk_level === 'High' ? 'var(--danger)' : 'var(--primary)'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                            <h3 style={{ margin: 0 }}>{trend.topic}</h3>
                            <span style={{
                                background: trend.risk_level === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(99, 102, 241, 0.2)',
                                color: trend.risk_level === 'High' ? 'var(--danger)' : 'var(--primary)',
                                padding: '0.25rem 0.75rem',
                                borderRadius: '1rem',
                                fontSize: '0.8rem',
                                fontWeight: 'bold'
                            }}>
                                {trend.risk_level.toUpperCase()}
                            </span>
                        </div>

                        <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{trend.description}</p>

                        <div style={{ fontSize: '0.9rem' }}>
                            <strong>Keywords:</strong> {trend.keywords.join(', ')}
                        </div>
                    </div>
                ))}
                {trends.length === 0 && <p className="text-muted">No active threats detected.</p>}
            </div>
        </div>
    );
}
