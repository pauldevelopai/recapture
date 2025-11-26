import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, ArrowLeft, Twitter, Instagram, Facebook, Video, RefreshCw, AlertTriangle, TrendingUp } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

export default function SubjectDetail() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [subject, setSubject] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [socialFeeds, setSocialFeeds] = useState([]);
    const [socialPosts, setSocialPosts] = useState([]);
    const [riskProfile, setRiskProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [scraping, setScraping] = useState(false);

    useEffect(() => {
        if (id) {
            fetchSubjectData();
        }
    }, [id]);

    const fetchSubjectData = async () => {
        try {
            setLoading(true);

            // Fetch subject info
            const subjectRes = await axios.get(`${API_URL}/subjects`);
            const subjectData = subjectRes.data.find(s => s.id === id);
            setSubject(subjectData);

            // Fetch social feeds
            const feedsRes = await axios.get(`${API_URL}/subjects/${id}/social-feeds`);
            setSocialFeeds(feedsRes.data);

            // Fetch social posts
            const postsRes = await axios.get(`${API_URL}/subjects/${id}/social-posts?limit=50`);
            setSocialPosts(postsRes.data);

            // Fetch risk profile
            try {
                const riskRes = await axios.get(`${API_URL}/subjects/${id}/risk-profile`);
                setRiskProfile(riskRes.data);
            } catch (err) {
                console.log("No risk profile yet");
            }

        } catch (err) {
            console.error("Error fetching subject data:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleScrapeFeeds = async () => {
        setScraping(true);
        try {
            await axios.post(`${API_URL}/subjects/${id}/scrape-feeds`);
            // Refresh data after scraping
            await fetchSubjectData();
        } catch (err) {
            console.error("Error scraping feeds:", err);
            alert("Error scraping social media feeds. Check API credentials.");
        } finally {
            setScraping(false);
        }
    };

    const handleGenerateRiskProfile = async () => {
        try {
            await axios.post(`${API_URL}/subjects/${id}/risk-profile`);
            await fetchSubjectData();
        } catch (err) {
            console.error("Error generating risk profile:", err);
        }
    };

    const getPlatformIcon = (platform) => {
        switch (platform.toLowerCase()) {
            case 'twitter': return <Twitter size={16} />;
            case 'instagram': return <Instagram size={16} />;
            case 'facebook': return <Facebook size={16} />;
            case 'tiktok': return <Video size={16} />;
            default: return <User size={16} />;
        }
    };

    const getRiskColor = (score) => {
        if (score < 30) return 'var(--success)';
        if (score < 60) return 'var(--warning)';
        return 'var(--danger)';
    };

    if (loading) {
        return <div className="subjects-page"><p>Loading...</p></div>;
    }

    if (!subject) {
        return <div className="subjects-page"><p>Subject not found</p></div>;
    }

    return (
        <div className="subjects-page">
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                <button onClick={() => navigate('/subjects')} style={{ padding: '0.5rem', minWidth: 'auto' }}>
                    <ArrowLeft size={20} />
                </button>
                <div style={{ flex: 1 }}>
                    <h1 style={{ margin: 0 }}>{subject.name}</h1>
                    <p className="text-muted">{subject.age} years old • {subject.risk_level} Risk</p>
                </div>
                <button onClick={() => navigate(`/subjects/${id}/clone`)} style={{ background: 'var(--primary)' }}>
                    Launch Digital Clone
                </button>
            </div>

            {/* Tabs */}
            <div style={{ borderBottom: '1px solid var(--border)', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', gap: '2rem' }}>
                    {['overview', 'social', 'posts', 'risk-profile'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                padding: '1rem',
                                borderBottom: activeTab === tab ? '2px solid var(--primary)' : '2px solid transparent',
                                color: activeTab === tab ? 'var(--text)' : 'var(--text-muted)',
                                cursor: 'pointer',
                                textTransform: 'capitalize'
                            }}
                        >
                            {tab.replace('-', ' ')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div className="card">
                    <h3>Subject Information</h3>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <div>
                            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>Risk Level</label>
                            <span style={{
                                padding: '0.5rem 1rem',
                                borderRadius: '0.5rem',
                                background: subject.risk_level === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                                color: subject.risk_level === 'High' ? 'var(--danger)' : 'var(--success)'
                            }}>
                                {subject.risk_level}
                            </span>
                        </div>
                        <div>
                            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.5rem' }}>Notes</label>
                            <p>{subject.notes || 'No notes added.'}</p>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'social' && (
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3>Social Media Accounts</h3>
                        <button onClick={handleScrapeFeeds} disabled={scraping || socialFeeds.length === 0}>
                            <RefreshCw size={16} style={{ marginRight: '0.5rem' }} />
                            {scraping ? 'Scraping...' : 'Refresh All Feeds'}
                        </button>
                    </div>

                    {socialFeeds.length === 0 ? (
                        <div className="card">
                            <p className="text-muted">No social media accounts connected yet.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {socialFeeds.map(feed => (
                                <div key={feed.id} className="card">
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                        <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}>
                                            {getPlatformIcon(feed.platform)}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <h4 style={{ margin: 0 }}>{feed.platform}</h4>
                                            <p className="text-muted" style={{ margin: '0.25rem 0 0 0' }}>
                                                @{feed.username || 'N/A'}
                                            </p>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <span style={{
                                                padding: '0.25rem 0.75rem',
                                                borderRadius: '1rem',
                                                fontSize: '0.875rem',
                                                background: feed.status === 'active' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                                color: feed.status === 'active' ? 'var(--success)' : 'var(--danger)'
                                            }}>
                                                {feed.status}
                                            </span>
                                            {feed.last_scraped && (
                                                <p className="text-muted" style={{ fontSize: '0.75rem', margin: '0.5rem 0 0 0' }}>
                                                    Last scraped: {new Date(feed.last_scraped).toLocaleString()}
                                                </p>
                                            )}
                                            {feed.error_message && (
                                                <p style={{ fontSize: '0.75rem', color: 'var(--danger)', margin: '0.5rem 0 0 0' }}>
                                                    {feed.error_message}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'posts' && (
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3>Social Media Posts ({socialPosts.length})</h3>
                    </div>

                    {socialPosts.length === 0 ? (
                        <div className="card">
                            <p className="text-muted">No posts scraped yet. Add social media accounts and refresh feeds.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '1rem' }}>
                            {socialPosts.map(post => (
                                <div key={post.id} className="card">
                                    <div style={{ display: 'flex', alignItems: 'start', gap: '1rem' }}>
                                        <div style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}>
                                            {getPlatformIcon(post.platform)}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
                                                <strong>{post.platform}</strong>
                                                <span className="text-muted" style={{ fontSize: '0.875rem' }}>
                                                    {post.posted_at && new Date(post.posted_at).toLocaleString()}
                                                </span>
                                            </div>
                                            <p style={{ margin: '0 0 0.5rem 0' }}>{post.content}</p>
                                            {post.url && (
                                                <a href={post.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.875rem', color: 'var(--primary)' }}>
                                                    View Original
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'risk-profile' && (
                <div>
                    {!riskProfile ? (
                        <div className="card">
                            <p className="text-muted">No risk profile generated yet.</p>
                            <button onClick={handleGenerateRiskProfile} style={{ marginTop: '1rem' }}>
                                Generate Risk Profile
                            </button>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '1.5rem' }}>
                            {/* Risk Score */}
                            <div className="card">
                                <h3>Overall Risk Score</h3>
                                <div style={{ textAlign: 'center', padding: '2rem' }}>
                                    <div style={{
                                        fontSize: '4rem',
                                        fontWeight: 'bold',
                                        color: getRiskColor(riskProfile.overall_risk_score)
                                    }}>
                                        {Math.round(riskProfile.overall_risk_score)}
                                    </div>
                                    <p className="text-muted">out of 100</p>
                                    <p className="text-muted" style={{ fontSize: '0.875rem' }}>
                                        Based on {riskProfile.post_count} social media posts
                                    </p>
                                </div>
                            </div>

                            {/* Detected Themes */}
                            {riskProfile.detected_themes && riskProfile.detected_themes.length > 0 && (
                                <div className="card">
                                    <h3>Detected Themes & Interests</h3>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                        {riskProfile.detected_themes.map((theme, idx) => (
                                            <span key={idx} style={{
                                                padding: '0.5rem 1rem',
                                                borderRadius: '1rem',
                                                background: 'rgba(255,255,255,0.1)',
                                                fontSize: '0.875rem'
                                            }}>
                                                {theme}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Risk Factors */}
                            {riskProfile.risk_factors && riskProfile.risk_factors.length > 0 && (
                                <div className="card">
                                    <h3>Risk Factors</h3>
                                    <div style={{ display: 'grid', gap: '1rem' }}>
                                        {riskProfile.risk_factors.map((factor, idx) => (
                                            <div key={idx} style={{
                                                padding: '1rem',
                                                background: 'rgba(255,255,255,0.05)',
                                                borderRadius: '0.5rem',
                                                borderLeft: `4px solid ${factor.severity === 'High' ? 'var(--danger)' : factor.severity === 'Medium' ? 'var(--warning)' : 'var(--success)'}`
                                            }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <strong>{factor.factor}</strong>
                                                    <span style={{
                                                        padding: '0.25rem 0.75rem',
                                                        borderRadius: '1rem',
                                                        fontSize: '0.75rem',
                                                        background: factor.severity === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(251, 191, 36, 0.2)',
                                                        color: factor.severity === 'High' ? 'var(--danger)' : 'var(--warning)'
                                                    }}>
                                                        {factor.severity}
                                                    </span>
                                                </div>
                                                {factor.evidence && (
                                                    <p className="text-muted" style={{ fontSize: '0.875rem', margin: 0, fontStyle: 'italic' }}>
                                                        "{factor.evidence}"
                                                    </p>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Language Patterns */}
                            {riskProfile.language_patterns && Object.keys(riskProfile.language_patterns).length > 0 && (
                                <div className="card">
                                    <h3>Language Patterns</h3>
                                    <div style={{ display: 'grid', gap: '0.75rem' }}>
                                        {Object.entries(riskProfile.language_patterns).map(([key, value]) => (
                                            <div key={key}>
                                                <strong style={{ textTransform: 'capitalize' }}>{key.replace('_', ' ')}:</strong>
                                                <span style={{ marginLeft: '0.5rem' }}>{value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
