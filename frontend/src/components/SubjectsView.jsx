
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { UserPlus, User, AlertTriangle, Plus, X, Search, LayoutGrid, Trash2 } from 'lucide-react';
import Scanner from './Scanner';
import SubjectDiscovery from './SubjectDiscovery';

export default function SubjectsView() {
    const navigate = useNavigate();
    const [subjects, setSubjects] = useState([]);
    const [activeTab, setActiveTab] = useState('profiles'); // 'profiles', 'scanner', or 'discovery'
    const [showForm, setShowForm] = useState(false);
    const [newSubject, setNewSubject] = useState({ name: '', age: '', risk_level: 'Low', notes: '' });
    const [socialFeeds, setSocialFeeds] = useState([{ platform: 'Twitter', username: '', profile_url: '' }]);

    useEffect(() => {
        fetchSubjects();
    }, []);

    const fetchSubjects = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/subjects');
            setSubjects(res.data);
        } catch (err) {
            console.error("Error fetching subjects:", err);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const subjectRes = await axios.post('http://127.0.0.1:8000/api/subjects', newSubject);
            const subjectId = subjectRes.data.id;

            // Add social media feeds - only add feeds with actual data
            for (const feed of socialFeeds) {
                if (feed.username && feed.username.trim()) {
                    const feedData = {
                        platform: feed.platform,
                        username: feed.username.trim(),
                        profile_url: feed.profile_url.trim() || `https://${feed.platform.toLowerCase()}.com/${feed.username.trim()}`
                    };

                    try {
                        await axios.post(`http://127.0.0.1:8000/api/subjects/${subjectId}/social-feeds`, feedData);
                    } catch (feedErr) {
                        console.error(`Error adding ${feed.platform} feed:`, feedErr);
                        // Continue adding other feeds even if one fails
                    }
                }
            }

            // Trigger initial scrape if any feeds were added
            const validFeeds = socialFeeds.filter(f => f.username && f.username.trim());
            if (validFeeds.length > 0) {
                try {
                    await axios.post(`http://127.0.0.1:8000/api/subjects/${subjectId}/scrape-feeds`);
                } catch (scrapeErr) {
                    console.log("Scraping error (expected if no API creds):", scrapeErr);
                }
            }

            setShowForm(false);
            setNewSubject({ name: '', age: '', risk_level: 'Low', notes: '' });
            setSocialFeeds([{ platform: 'Twitter', username: '', profile_url: '' }]);
            fetchSubjects();
        } catch (err) {
            console.error("Error creating subject:", err);
            alert("Error creating subject. Check console for details.");
        }
    };

    const addFeedInput = () => {
        setSocialFeeds([...socialFeeds, { platform: 'Twitter', username: '', profile_url: '' }]);
    };

    const removeFeedInput = (index) => {
        setSocialFeeds(socialFeeds.filter((_, i) => i !== index));
    };

    const updateFeed = (index, field, value) => {
        const updated = [...socialFeeds];
        updated[index][field] = value;
        setSocialFeeds(updated);
    };

    return (
        <div className="subjects-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1>Subjects</h1>
                    <p className="text-muted">Manage the profiles of the young people you are protecting. Create Digital Clones to test arguments.</p>
                </div>
                {activeTab === 'profiles' && (
                    <button onClick={() => setShowForm(!showForm)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <UserPlus size={18} /> Add Subject
                    </button>
                )}
            </div>

            {/* Tabs */}
            <div style={{ borderBottom: '1px solid var(--border)', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', gap: '2rem' }}>
                    <button
                        onClick={() => setActiveTab('profiles')}
                        style={{
                            padding: '1rem',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'profiles' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'profiles' ? 'var(--text)' : 'var(--text-muted)',
                            cursor: 'pointer'
                        }}
                    >
                        Profiles
                    </button>
                    <button
                        onClick={() => setActiveTab('scanner')}
                        style={{
                            padding: '1rem',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'scanner' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'scanner' ? 'var(--text)' : 'var(--text-muted)',
                            cursor: 'pointer'
                        }}
                    >
                        Digital Diet Scanner
                    </button>
                    <button
                        onClick={() => setActiveTab('discovery')}
                        style={{
                            padding: '1rem',
                            background: 'transparent',
                            border: 'none',
                            borderBottom: activeTab === 'discovery' ? '2px solid var(--primary)' : '2px solid transparent',
                            color: activeTab === 'discovery' ? 'var(--text)' : 'var(--text-muted)',
                            cursor: 'pointer'
                        }}
                    >
                        Subject Discovery
                    </button>
                </div>
            </div>

            {activeTab === 'scanner' && <Scanner />}
            {activeTab === 'discovery' && <SubjectDiscovery />}
            {activeTab === 'profiles' && (
                <>
                    {showForm && (
                        <div className="card" style={{ marginBottom: '2rem', border: '1px solid var(--primary)' }}>
                            <h3>New Subject</h3>
                            <form onSubmit={handleCreate} style={{ display: 'grid', gap: '1rem' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                    <input
                                        placeholder="Name"
                                        value={newSubject.name}
                                        onChange={e => setNewSubject({ ...newSubject, name: e.target.value })}
                                        required
                                    />
                                    <input
                                        type="number"
                                        placeholder="Age"
                                        value={newSubject.age}
                                        onChange={e => setNewSubject({ ...newSubject, age: e.target.value })}
                                        required
                                    />
                                </div>
                                <select
                                    value={newSubject.risk_level}
                                    onChange={e => setNewSubject({ ...newSubject, risk_level: e.target.value })}
                                    style={{ padding: '0.75rem', borderRadius: 'var(--radius)', background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)' }}
                                >
                                    <option value="Low">Low Risk</option>
                                    <option value="Medium">Medium Risk</option>
                                    <option value="High">High Risk</option>
                                </select>
                                <textarea
                                    placeholder="Notes / Context"
                                    value={newSubject.notes}
                                    onChange={e => setNewSubject({ ...newSubject, notes: e.target.value })}
                                />

                                <div>
                                    <h4 style={{ marginBottom: '1rem' }}>Social Media Accounts (Optional)</h4>
                                    {socialFeeds.map((feed, idx) => (
                                        <div key={idx} style={{ display: 'grid', gridTemplateColumns: '150px 1fr 1fr auto', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                            <select
                                                value={feed.platform}
                                                onChange={e => updateFeed(idx, 'platform', e.target.value)}
                                                style={{ padding: '0.75rem', borderRadius: 'var(--radius)', background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)' }}
                                            >
                                                <option value="Twitter">Twitter</option>
                                                <option value="Instagram">Instagram</option>
                                                <option value="TikTok">TikTok</option>
                                                <option value="Facebook">Facebook</option>
                                            </select>
                                            <input
                                                placeholder="Username"
                                                value={feed.username}
                                                onChange={e => updateFeed(idx, 'username', e.target.value)}
                                            />
                                            <input
                                                placeholder="Profile URL (optional)"
                                                value={feed.profile_url}
                                                onChange={e => updateFeed(idx, 'profile_url', e.target.value)}
                                            />
                                            <button
                                                type="button"
                                                onClick={() => removeFeedInput(idx)}
                                                style={{ minWidth: 'auto', padding: '0.75rem', background: 'var(--danger)' }}
                                            >
                                                <X size={18} />
                                            </button>
                                        </div>
                                    ))}
                                    <button type="button" onClick={addFeedInput} style={{ marginTop: '0.5rem', background: 'var(--border)' }}>
                                        <Plus size={16} style={{ marginRight: '0.5rem' }} />
                                        Add Another Account
                                    </button>
                                </div>

                                <button type="submit">Save Subject</button>
                            </form>
                        </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                        {subjects.map(subject => (
                            <div
                                key={subject.id}
                                className="card"
                                style={{ cursor: 'pointer', transition: 'transform 0.2s' }}
                                onClick={() => navigate(`/subjects/${subject.id}`)}
                                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                                onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}>
                                            <User size={24} />
                                        </div>
                                        <div>
                                            <h3 style={{ margin: 0 }}>{subject.name}</h3>
                                            <span className="text-muted">{subject.age} years old</span>
                                        </div>
                                    </div>
                                    <span style={{
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '1rem',
                                        fontSize: '0.875rem',
                                        background: subject.risk_level === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                                        color: subject.risk_level === 'High' ? 'var(--danger)' : 'var(--success)'
                                    }}>
                                        {subject.risk_level} Risk
                                    </span>
                                </div>
                                <p className="text-muted">{subject.notes || "No notes added."}</p>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
