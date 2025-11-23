import { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Database, Plus, Trash2, Play, Check, X, RefreshCw, Rss, Globe,
    AlertTriangle, Search, Activity, Smartphone, Clock, ShieldAlert, LayoutDashboard
} from 'lucide-react';

export default function IntelCenter() {
    const [activeTab, setActiveTab] = useState('dashboard');

    // --- DataLab State ---
    const [sources, setSources] = useState([]);
    const [topics, setTopics] = useState([]);
    const [content, setContent] = useState([]);
    const [loadingPipeline, setLoadingPipeline] = useState(false);
    const [loadingBatchTrain, setLoadingBatchTrain] = useState(false);
    const [modelStats, setModelStats] = useState({ total_documents: 0 });
    const [newSourceUrl, setNewSourceUrl] = useState('');
    const [newSourceType, setNewSourceType] = useState('direct');
    const [newTopic, setNewTopic] = useState('');

    // --- ActivityMonitor State ---
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState('');
    const [logs, setLogs] = useState([]);
    const [simulatedContent, setSimulatedContent] = useState('');
    const [isScanning, setIsScanning] = useState(false);

    // --- ThreatMonitor State ---
    const [trends, setTrends] = useState([]);
    const [loadingTrends, setLoadingTrends] = useState(true);

    useEffect(() => {
        // Initial Fetch
        fetchSources();
        fetchTopics();
        fetchContent();
        fetchProfiles();
        fetchTrends();
        fetchModelStats();
    }, []);

    useEffect(() => {
        if (selectedProfile) {
            fetchLogs(selectedProfile);
            const interval = setInterval(() => fetchLogs(selectedProfile), 3000);
            return () => clearInterval(interval);
        }
    }, [selectedProfile]);

    // --- API Calls ---
    const fetchSources = async () => { try { setSources((await axios.get('http://127.0.0.1:8000/sources')).data); } catch (e) { console.error(e); } };
    const fetchTopics = async () => { try { setTopics((await axios.get('http://127.0.0.1:8000/topics')).data); } catch (e) { console.error(e); } };
    const fetchContent = async () => { try { setContent((await axios.get('http://127.0.0.1:8000/pipeline/content')).data); } catch (e) { console.error(e); } };
    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/profiles');
            setProfiles(res.data);
            if (res.data.length > 0 && !selectedProfile) setSelectedProfile(res.data[0].id);
        } catch (e) { console.error(e); }
    };
    const fetchLogs = async (pid) => { try { setLogs((await axios.get(`http://127.0.0.1:8000/api/profiles/${pid}/logs`)).data); } catch (e) { console.error(e); } };
    const fetchTrends = async () => { try { setTrends((await axios.get('http://127.0.0.1:8000/trends')).data); } catch (e) { console.error(e); } finally { setLoadingTrends(false); } };
    const fetchModelStats = async () => { try { setModelStats((await axios.get('http://127.0.0.1:8000/pipeline/stats')).data); } catch (e) { console.error(e); } };

    // --- Handlers ---
    const handleAddSource = async () => {
        if (!newSourceUrl) return;
        try {
            await axios.post('http://127.0.0.1:8000/sources', { name: newSourceUrl, url: newSourceUrl, type: newSourceType });
            setNewSourceUrl(''); fetchSources();
        } catch (e) { alert("Failed to add source"); }
    };

    const handleAddTopic = async () => {
        if (!newTopic) return;
        try {
            await axios.post(`http://127.0.0.1:8000/topics?topic=${encodeURIComponent(newTopic)}`);
            setNewTopic(''); fetchTopics();
        } catch (e) { alert("Failed to add topic"); }
    };

    const handleDeleteSource = async (id) => { try { await axios.delete(`http://127.0.0.1:8000/sources/${id}`); fetchSources(); } catch (e) { console.error(e); } };

    const handleRunPipeline = async () => {
        setLoadingPipeline(true);
        try { await axios.post('http://127.0.0.1:8000/pipeline/run'); await fetchContent(); alert("Pipeline run complete!"); }
        catch (e) { alert("Pipeline failed."); }
        finally { setLoadingPipeline(false); }
    };

    const handleApprove = async (id) => { try { await axios.post(`http://127.0.0.1:8000/pipeline/content/${id}/approve`); fetchContent(); } catch (e) { console.error(e); } };
    const handleDiscard = async (id) => { try { await axios.post(`http://127.0.0.1:8000/pipeline/content/${id}/discard`); fetchContent(); } catch (e) { console.error(e); } };

    const handleBatchTrain = async () => {
        setLoadingBatchTrain(true);
        try {
            const result = await axios.post('http://127.0.0.1:8000/pipeline/train-batch');
            alert(`✅ ${result.data.message}\n\nTotal documents in model: ${result.data.total_documents}`);
            fetchContent();
            fetchModelStats();
        } catch (e) { alert("Batch training failed."); }
        finally { setLoadingBatchTrain(false); }
    };

    const handleSimulateIngestion = async () => {
        if (!simulatedContent.trim() || !selectedProfile) return;
        setIsScanning(true);
        try {
            await axios.post('http://127.0.0.1:8000/api/scanner/ingest', {
                profile_id: selectedProfile, content: simulatedContent, source_url: "Simulated Device Input", timestamp: new Date().toISOString()
            });
            setSimulatedContent(''); fetchLogs(selectedProfile);
        } catch (e) { console.error(e); } finally { setIsScanning(false); }
    };

    // --- Derived Stats for Dashboard ---
    const totalTime = (logs || []).length * 5; // Mock calculation
    const avgRisk = (logs || []).length > 0 ? (logs || []).reduce((acc, l) => acc + (l.risk_score || 0), 0) / logs.length : 0;

    return (
        <div className="intel-center">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1>Intel Center</h1>
                    <p className="text-muted">Unified command for threat intelligence, monitoring, and analysis.</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                        onClick={() => setActiveTab('dashboard')}
                        style={{ background: activeTab === 'dashboard' ? 'var(--primary)' : 'var(--surface)', color: 'white', padding: '0.5rem 1rem', borderRadius: 'var(--radius)' }}
                    >
                        <LayoutDashboard size={16} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Dashboard
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
                        onClick={() => setActiveTab('activity')}
                        style={{ background: activeTab === 'activity' ? 'var(--primary)' : 'var(--surface)', color: 'white', padding: '0.5rem 1rem', borderRadius: 'var(--radius)' }}
                    >
                        <Activity size={16} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Live Activity
                    </button>
                    <button
                        className={`tab-btn ${activeTab === 'management' ? 'active' : ''}`}
                        onClick={() => setActiveTab('management')}
                        style={{ background: activeTab === 'management' ? 'var(--primary)' : 'var(--surface)', color: 'white', padding: '0.5rem 1rem', borderRadius: 'var(--radius)' }}
                    >
                        <Database size={16} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Management
                    </button>
                </div>
            </div>

            {/* --- DASHBOARD TAB --- */}
            {activeTab === 'dashboard' && (
                <div className="dashboard-tab">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
                        <div className="card">
                            <h3><Clock size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Time Spent (Today)</h3>
                            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)', margin: '1rem 0' }}>
                                {totalTime} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>min</span>
                            </div>
                        </div>
                        <div className="card">
                            <h3><AlertTriangle size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Avg Risk Score</h3>
                            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: avgRisk > 0.5 ? 'var(--danger)' : 'var(--success)', margin: '1rem 0' }}>
                                {(avgRisk * 10).toFixed(1)} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/ 10</span>
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h2>Active Threats</h2>
                        <button
                            className="btn btn-primary"
                            onClick={async () => {
                                setLoadingTrends(true);
                                try { await axios.post('http://127.0.0.1:8000/trends/refresh'); await fetchTrends(); }
                                catch (e) { alert("Failed to refresh trends"); }
                                finally { setLoadingTrends(false); }
                            }}
                            disabled={loadingTrends}
                            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                        >
                            {loadingTrends ? <RefreshCw className="animate-spin" size={16} /> : <Globe size={16} />}
                            Refresh Trends (Real-time)
                        </button>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
                        {(trends || []).map(trend => (
                            <div key={trend.id} className="card" style={{ borderTop: `4px solid ${trend.risk_level === 'High' ? 'var(--danger)' : 'var(--primary)'}` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                    <h3 style={{ margin: 0 }}>{trend.topic}</h3>
                                    <span style={{ background: trend.risk_level === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(99, 102, 241, 0.2)', color: trend.risk_level === 'High' ? 'var(--danger)' : 'var(--primary)', padding: '0.25rem 0.75rem', borderRadius: '1rem', fontSize: '0.8rem', fontWeight: 'bold' }}>
                                        {(trend.risk_level || 'UNKNOWN').toUpperCase()}
                                    </span>
                                </div>
                                <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>{trend.description}</p>
                                {trend.sources && trend.sources.length > 0 && (
                                    <div style={{ fontSize: '0.85rem', borderTop: '1px solid var(--border)', paddingTop: '0.5rem' }}>
                                        <strong>Sources:</strong>
                                        <ul style={{ margin: '0.5rem 0 0 1.2rem', padding: 0, color: 'var(--text-muted)' }}>
                                            {trend.sources.map((s, i) => (
                                                <li key={i}><a href={s} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>{s.substring(0, 40)}...</a></li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                                <button
                                    className="btn"
                                    style={{ marginTop: '1rem', width: '100%', background: 'rgba(255,255,255,0.1)', border: '1px solid var(--border)' }}
                                    onClick={async () => {
                                        try {
                                            await axios.post(`http://127.0.0.1:8000/trends/${trend.id}/queue`);
                                            alert("Added to Training Queue!");
                                            fetchContent(); // Refresh queue
                                        } catch (e) { alert("Failed to add to queue"); }
                                    }}
                                >
                                    <Plus size={16} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />
                                    Add to Training Queue
                                </button>
                            </div>
                        ))}
                        {(trends || []).length === 0 && <p className="text-muted">No active threats detected.</p>}
                    </div>

                    {/* Training Queue Section */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
                        <div>
                            <h2>Training Queue (RAG)</h2>
                            <p className="text-muted" style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                                {content.filter(c => c.status === 'approved').length} approved items ready for batch training
                            </p>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button
                                className="btn"
                                onClick={handleBatchTrain}
                                disabled={loadingBatchTrain || content.filter(c => c.status === 'approved').length === 0}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    background: 'var(--success)',
                                    color: 'white',
                                    border: 'none'
                                }}
                            >
                                {loadingBatchTrain ? <RefreshCw className="animate-spin" size={18} /> : <Database size={18} />}
                                Train Model (Batch)
                            </button>
                            <button className="btn btn-primary" onClick={handleRunPipeline} disabled={loadingPipeline} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                {loadingPipeline ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />} Fetch New Intel
                            </button>
                        </div>
                    </div>

                    {/* Model Stats Card */}
                    <div className="card" style={{ marginBottom: '1rem', background: 'rgba(99, 102, 241, 0.1)', borderLeft: '4px solid var(--primary)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <strong style={{ color: 'var(--primary)' }}><Database size={16} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />Model Knowledge Base</strong>
                                <p className="text-muted" style={{ margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>Total documents trained</p>
                            </div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{modelStats.total_documents}</div>
                        </div>
                    </div>

                    <div className="inbox-list">
                        {content.filter(c => c.status === 'pending').slice(0, 3).map(item => (
                            <div key={item.id} className="card" style={{ marginBottom: '1rem', borderLeft: item.risk_score > 0.5 ? '4px solid var(--danger)' : '4px solid var(--success)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span className="badge" style={{
                                        background: item.status === 'approved' ? 'rgba(34, 197, 94, 0.2)' :
                                            item.status === 'trained' ? 'rgba(99, 102, 241, 0.2)' :
                                                'rgba(255,255,255,0.1)',
                                        color: item.status === 'approved' ? 'var(--success)' :
                                            item.status === 'trained' ? 'var(--primary)' :
                                                'white'
                                    }}>{item.status.toUpperCase()}</span>
                                    <span className="text-muted" style={{ fontSize: '0.8rem' }}>{new Date(item.timestamp).toLocaleString()}</span>
                                </div>
                                <p style={{ marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>{item.content.substring(0, 300)}...</p>
                                {item.analysis_summary && <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.9rem' }}><strong>AI Analysis:</strong> {item.analysis_summary}</div>}
                                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                                    <button onClick={() => handleDiscard(item.id)} className="btn" style={{ background: 'transparent', border: '1px solid var(--danger)', color: 'var(--danger)' }}><X size={16} /> Discard</button>
                                    <button onClick={() => handleApprove(item.id)} className="btn" style={{ background: 'var(--success)', border: 'none', color: 'white' }}><Check size={16} /> Approve</button>
                                </div>
                            </div>
                        ))}
                        {content.filter(c => c.status === 'pending').length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '2rem' }}>No pending items to review.</p>}
                        {content.filter(c => c.status === 'pending').length > 3 && (
                            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                                <button className="btn" onClick={() => setActiveTab('management')} style={{ color: 'var(--primary)' }}>View all pending items in Management tab &rarr;</button>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* --- LIVE ACTIVITY TAB --- */}
            {activeTab === 'activity' && (
                <div className="activity-tab">
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
                        <select value={selectedProfile} onChange={(e) => setSelectedProfile(e.target.value)} style={{ padding: '0.75rem', borderRadius: 'var(--radius)', minWidth: '200px' }}>
                            {profiles.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '2rem' }}>
                        <div className="card">
                            <h3>Recent Activity Log</h3>
                            <div className="list">
                                {logs.map(log => (
                                    <div key={log.id} style={{ padding: '1rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                                        <div>
                                            <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>{log.platform}</div>
                                            <div className="text-muted" style={{ fontSize: '0.9rem' }}>{new Date(log.timestamp).toLocaleString()}</div>
                                        </div>
                                        <div style={{ padding: '0.25rem 0.75rem', borderRadius: '1rem', background: log.risk_score > 0.5 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)', color: log.risk_score > 0.5 ? 'var(--danger)' : 'var(--success)', fontSize: '0.9rem', fontWeight: 'bold' }}>
                                            Risk: {(log.risk_score * 10).toFixed(1)}
                                        </div>
                                    </div>
                                ))}
                                {logs.length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '1rem' }}>No activity recorded yet.</p>}
                            </div>
                        </div>
                        <div>
                            <div className="card" style={{ position: 'sticky', top: '1rem' }}>
                                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: 0 }}><Smartphone size={20} /> Simulator</h3>
                                <textarea value={simulatedContent} onChange={(e) => setSimulatedContent(e.target.value)} placeholder="Paste text content here..." rows={5} style={{ marginBottom: '1rem' }} />
                                <button onClick={handleSimulateIngestion} disabled={isScanning || !simulatedContent.trim()} style={{ width: '100%' }}>{isScanning ? 'Scanning...' : 'Ingest Content'}</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* --- MANAGEMENT TAB --- */}
            {activeTab === 'management' && (
                <div className="management-tab">
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                        <div className="card" style={{ flex: 1, minWidth: '300px' }}>
                            <h3>Add Topic</h3>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <input type="text" value={newTopic} onChange={(e) => setNewTopic(e.target.value)} placeholder="e.g. 'Flat Earth'" style={{ flex: 1 }} />
                                <button onClick={handleAddTopic} disabled={!newTopic}><Plus size={18} /></button>
                            </div>
                            <div style={{ marginTop: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                {topics.map((t, i) => <span key={i} style={{ background: 'var(--surface)', border: '1px solid var(--border)', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>{t}</span>)}
                            </div>
                        </div>
                        <div className="card" style={{ flex: 1, minWidth: '300px' }}>
                            <h3>Add Source</h3>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <input type="text" value={newSourceUrl} onChange={(e) => setNewSourceUrl(e.target.value)} placeholder="URL..." style={{ flex: 1 }} />
                                <button onClick={handleAddSource} disabled={!newSourceUrl}><Plus size={18} /></button>
                            </div>
                            <div style={{ marginTop: '1rem', maxHeight: '100px', overflowY: 'auto' }}>
                                {sources.map(s => <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '0.5rem' }}><span>{s.name}</span><Trash2 size={14} onClick={() => handleDeleteSource(s.id)} style={{ cursor: 'pointer', color: 'var(--danger)' }} /></div>)}
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h2>Data Inbox</h2>
                        <button className="btn btn-primary" onClick={handleRunPipeline} disabled={loadingPipeline} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {loadingPipeline ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />} Run Pipeline
                        </button>
                    </div>

                    <div className="inbox-list">
                        {content.filter(c => c.status === 'pending').map(item => (
                            <div key={item.id} className="card" style={{ marginBottom: '1rem', borderLeft: item.risk_score > 0.5 ? '4px solid var(--danger)' : '4px solid var(--success)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <span className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{item.status.toUpperCase()}</span>
                                    <span className="text-muted" style={{ fontSize: '0.8rem' }}>{new Date(item.timestamp).toLocaleString()}</span>
                                </div>
                                <p style={{ marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>{item.content.substring(0, 300)}...</p>
                                {item.analysis_summary && <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.9rem' }}><strong>AI Analysis:</strong> {item.analysis_summary}</div>}
                                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                                    <button onClick={() => handleDiscard(item.id)} className="btn" style={{ background: 'transparent', border: '1px solid var(--danger)', color: 'var(--danger)' }}><X size={16} /> Discard</button>
                                    <button onClick={() => handleApprove(item.id)} className="btn" style={{ background: 'var(--success)', border: 'none', color: 'white' }}><Check size={16} /> Approve</button>
                                </div>
                            </div>
                        ))}
                        {content.filter(c => c.status === 'pending').length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '2rem' }}>No pending items.</p>}
                    </div>
                </div>
            )}
        </div>
    );
}
