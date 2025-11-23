import { useState, useEffect } from 'react';
import axios from 'axios';
import { Database, Plus, Trash2, Play, Check, X, RefreshCw, Rss, Globe, AlertTriangle, Search } from 'lucide-react';

export default function DataLab() {
    const [activeTab, setActiveTab] = useState('inbox');
    const [sources, setSources] = useState([]);
    const [topics, setTopics] = useState([]);
    const [content, setContent] = useState([]);
    const [loading, setLoading] = useState(false);
    const [newSourceUrl, setNewSourceUrl] = useState('');
    const [newSourceType, setNewSourceType] = useState('direct');
    const [newTopic, setNewTopic] = useState('');

    useEffect(() => {
        fetchSources();
        fetchTopics();
        fetchContent();
    }, []);

    const fetchSources = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/sources');
            setSources(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchTopics = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/topics');
            setTopics(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchContent = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/pipeline/content');
            setContent(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleAddSource = async () => {
        if (!newSourceUrl) return;
        try {
            await axios.post('http://127.0.0.1:8000/sources', {
                name: newSourceUrl, // Simple name for now
                url: newSourceUrl,
                type: newSourceType
            });
            setNewSourceUrl('');
            fetchSources();
        } catch (err) {
            alert("Failed to add source");
        }
    };

    const handleAddTopic = async () => {
        if (!newTopic) return;
        try {
            await axios.post(`http://127.0.0.1:8000/topics?topic=${encodeURIComponent(newTopic)}`);
            setNewTopic('');
            fetchTopics();
        } catch (err) {
            alert("Failed to add topic");
        }
    };

    const handleDeleteSource = async (id) => {
        try {
            await axios.delete(`http://127.0.0.1:8000/sources/${id}`);
            fetchSources();
        } catch (err) {
            console.error(err);
        }
    };

    const handleRunPipeline = async () => {
        setLoading(true);
        try {
            await axios.post('http://127.0.0.1:8000/pipeline/run');
            await fetchContent();
            alert("Pipeline run complete! Check Inbox.");
        } catch (err) {
            alert("Pipeline failed to run.");
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (id) => {
        try {
            await axios.post(`http://127.0.0.1:8000/pipeline/content/${id}/approve`);
            fetchContent();
        } catch (err) {
            console.error(err);
        }
    };

    const handleDiscard = async (id) => {
        try {
            await axios.post(`http://127.0.0.1:8000/pipeline/content/${id}/discard`);
            fetchContent();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="datalab-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1>Threat Intel Lab</h1>
                    <p className="text-muted">Ingest, curate, and train the system on harmful content.</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={handleRunPipeline}
                    disabled={loading}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    {loading ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />}
                    Run Pipeline
                </button>
            </div>

            <div className="tabs" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
                <button
                    id="tab-inbox"
                    className={`tab-btn ${activeTab === 'inbox' ? 'active' : ''}`}
                    onClick={() => setActiveTab('inbox')}
                    style={{
                        padding: '0.5rem 1rem',
                        background: 'none',
                        border: 'none',
                        borderBottom: activeTab === 'inbox' ? '2px solid var(--primary)' : 'none',
                        color: activeTab === 'inbox' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer'
                    }}
                >
                    Data Inbox ({content.filter(c => c.status === 'pending').length})
                </button>
                <button
                    id="tab-topics"
                    className={`tab-btn ${activeTab === 'topics' ? 'active' : ''}`}
                    onClick={() => setActiveTab('topics')}
                    style={{
                        padding: '0.5rem 1rem',
                        background: 'none',
                        border: 'none',
                        borderBottom: activeTab === 'topics' ? '2px solid var(--primary)' : 'none',
                        color: activeTab === 'topics' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer'
                    }}
                >
                    Topics ({topics.length})
                </button>
                <button
                    id="tab-sources"
                    className={`tab-btn ${activeTab === 'sources' ? 'active' : ''}`}
                    onClick={() => setActiveTab('sources')}
                    style={{
                        padding: '0.5rem 1rem',
                        background: 'none',
                        border: 'none',
                        borderBottom: activeTab === 'sources' ? '2px solid var(--primary)' : 'none',
                        color: activeTab === 'sources' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer'
                    }}
                >
                    Sources ({sources.length})
                </button>
            </div>

            {activeTab === 'topics' && (
                <div className="card">
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                        <input
                            type="text"
                            className="input"
                            placeholder="Enter topic to monitor (e.g., 'Flat Earth')..."
                            value={newTopic}
                            onChange={(e) => setNewTopic(e.target.value)}
                            style={{ flex: 1 }}
                        />
                        <button className="btn btn-primary" onClick={handleAddTopic} disabled={!newTopic}>
                            <Plus size={18} /> Add Topic
                        </button>
                    </div>

                    <div className="list">
                        {topics.map((topic, index) => (
                            <div key={index} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '1rem', borderBottom: '1px solid var(--border)'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <Search size={20} color="var(--primary)" />
                                    <div style={{ fontWeight: 'bold' }}>{topic}</div>
                                </div>
                            </div>
                        ))}
                        {topics.length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '1rem' }}>No topics monitored yet.</p>}
                    </div>
                </div>
            )}

            {activeTab === 'sources' && (
                <div className="card">
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                        <select
                            className="input"
                            value={newSourceType}
                            onChange={(e) => setNewSourceType(e.target.value)}
                            style={{ width: '150px' }}
                        >
                            <option value="direct">Direct URL</option>
                            <option value="rss">RSS Feed</option>
                        </select>
                        <input
                            type="text"
                            className="input"
                            placeholder="Enter URL..."
                            value={newSourceUrl}
                            onChange={(e) => setNewSourceUrl(e.target.value)}
                            style={{ flex: 1, minWidth: '200px' }}
                        />
                        <button className="btn btn-primary" onClick={handleAddSource} disabled={!newSourceUrl}>
                            <Plus size={18} /> Add
                        </button>
                    </div>

                    <div className="list">
                        {sources.map(source => (
                            <div key={source.id} style={{
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                padding: '1rem', borderBottom: '1px solid var(--border)'
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    {source.type === 'rss' ? <Rss size={20} color="orange" /> : <Globe size={20} color="cyan" />}
                                    <div>
                                        <div style={{ fontWeight: 'bold' }}>{source.name}</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{source.url}</div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleDeleteSource(source.id)}
                                    style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        ))}
                        {sources.length === 0 && <p className="text-muted" style={{ textAlign: 'center', padding: '1rem' }}>No sources added yet.</p>}
                    </div>
                </div>
            )}

            {activeTab === 'inbox' && (
                <div className="inbox-list">
                    {content.filter(c => c.status === 'pending').map(item => (
                        <div key={item.id} className="card" style={{ marginBottom: '1rem', borderLeft: item.risk_score > 0.5 ? '4px solid var(--danger)' : '4px solid var(--success)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{item.status.toUpperCase()}</span>
                                <span className="text-muted" style={{ fontSize: '0.8rem' }}>{new Date(item.timestamp).toLocaleString()}</span>
                            </div>

                            <p style={{ marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>{item.content.substring(0, 300)}...</p>

                            {item.analysis_summary && (
                                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem', borderRadius: '4px', marginBottom: '1rem', fontSize: '0.9rem' }}>
                                    <strong>AI Analysis:</strong> {item.analysis_summary}
                                </div>
                            )}

                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                                <button
                                    onClick={() => handleDiscard(item.id)}
                                    className="btn"
                                    style={{ background: 'transparent', border: '1px solid var(--danger)', color: 'var(--danger)' }}
                                >
                                    <X size={16} style={{ marginRight: '0.25rem' }} /> Discard
                                </button>
                                <button
                                    onClick={() => handleApprove(item.id)}
                                    className="btn"
                                    style={{ background: 'var(--success)', border: 'none', color: 'white' }}
                                >
                                    <Check size={16} style={{ marginRight: '0.25rem' }} /> Approve & Train
                                </button>
                            </div>
                        </div>
                    ))}
                    {content.filter(c => c.status === 'pending').length === 0 && (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <Check size={48} color="var(--success)" style={{ marginBottom: '1rem' }} />
                            <h3>All Caught Up!</h3>
                            <p className="text-muted">No pending data to review. Run the pipeline to fetch more.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
