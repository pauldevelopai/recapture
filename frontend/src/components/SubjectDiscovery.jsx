import React, { useState } from 'react';
import { Search, UserPlus, AlertTriangle, Check, Loader } from 'lucide-react';
import axios from 'axios';

export default function SubjectDiscovery() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [importing, setImporting] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/discovery/search?query=${encodeURIComponent(query)}`);
            setResults(res.data);
        } catch (err) {
            console.error("Search failed:", err);
            alert("Failed to search for subjects.");
        } finally {
            setLoading(false);
        }
    };

    const handleImport = async (profile) => {
        setImporting(profile.username);
        try {
            await axios.post('http://127.0.0.1:8000/api/discovery/import', profile);
            // Mark as imported in local state
            setResults(results.map(r =>
                r.username === profile.username ? { ...r, imported: true } : r
            ));
            alert(`Successfully imported ${profile.username} as a subject!`);
        } catch (err) {
            console.error("Import failed:", err);
            alert("Failed to import subject.");
        } finally {
            setImporting(null);
        }
    };

    return (
        <div className="card" style={{ marginTop: '2rem' }}>
            <div style={{ marginBottom: '1.5rem' }}>
                <h3>Subject Discovery</h3>
                <p className="text-muted">Find potential at-risk subjects from social media based on keywords.</p>
            </div>

            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                    <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input
                        type="text"
                        className="input"
                        style={{ paddingLeft: '2.5rem', width: '100%' }}
                        placeholder="Search keywords (e.g., 'hopeless', 'incel', 'blackpill', 'lonely')"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? <Loader className="spin" size={20} /> : 'Search'}
                </button>
            </form>

            {results.length > 0 && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {results.map((profile, i) => (
                        <div key={i} style={{
                            padding: '1rem',
                            background: 'var(--background)',
                            borderRadius: '8px',
                            border: '1px solid var(--border)',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                        }}>
                            <div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <h4 style={{ margin: 0 }}>@{profile.username}</h4>
                                    <span style={{
                                        fontSize: '0.75rem',
                                        padding: '0.1rem 0.5rem',
                                        borderRadius: '1rem',
                                        background: 'var(--surface)',
                                        border: '1px solid var(--border)'
                                    }}>
                                        {profile.platform}
                                    </span>
                                </div>
                                <p style={{ margin: '0.5rem 0', fontSize: '0.9rem' }}>"{profile.sample_post}"</p>
                                {profile.url && (
                                    <a href={profile.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.8rem', color: 'var(--primary)', display: 'block', marginBottom: '0.5rem' }}>
                                        View Source
                                    </a>
                                )}
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    {profile.risk_indicators.map((tag, idx) => (
                                        <span key={idx} style={{
                                            fontSize: '0.75rem',
                                            color: 'var(--danger)',
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            padding: '0.1rem 0.4rem',
                                            borderRadius: '4px'
                                        }}>
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <button
                                className={`btn ${profile.imported ? '' : 'btn-primary'}`}
                                disabled={profile.imported || importing === profile.username}
                                onClick={() => handleImport(profile)}
                                style={{ minWidth: '120px' }}
                            >
                                {profile.imported ? (
                                    <>
                                        <Check size={16} style={{ marginRight: '0.5rem' }} /> Imported
                                    </>
                                ) : importing === profile.username ? (
                                    <Loader className="spin" size={16} />
                                ) : (
                                    <>
                                        <UserPlus size={16} style={{ marginRight: '0.5rem' }} /> Import
                                    </>
                                )}
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {!loading && results.length === 0 && query && (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No subjects found matching "{query}". Try different keywords.
                </div>
            )}
        </div>
    );
}
