import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserCheck, Plus, Trash2, Users } from 'lucide-react';

export default function AuthoritiesView() {
    const [profiles, setProfiles] = useState([]);
    const [selectedProfile, setSelectedProfile] = useState('');
    const [authorities, setAuthorities] = useState([]);
    const [newAuthority, setNewAuthority] = useState({ name: '', role: '', relation: '' });
    const [isAdding, setIsAdding] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfiles();
    }, []);

    useEffect(() => {
        if (selectedProfile) {
            fetchAuthorities(selectedProfile);
        } else {
            setAuthorities([]);
        }
    }, [selectedProfile]);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/profiles');
            setProfiles(res.data);
            if (res.data.length > 0) setSelectedProfile(res.data[0].id);
        } catch (e) { console.error("Failed to fetch profiles", e); }
    };

    const fetchAuthorities = async (pid) => {
        setLoading(true);
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/profiles/${pid}/authorities`);
            setAuthorities(res.data);
        } catch (e) { console.error("Failed to fetch authorities", e); }
        finally { setLoading(false); }
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newAuthority.name || !selectedProfile) return;

        try {
            await axios.post(`http://127.0.0.1:8000/api/profiles/${selectedProfile}/authorities`, {
                ...newAuthority,
                profile_id: selectedProfile
            });
            setNewAuthority({ name: '', role: '', relation: '' });
            setIsAdding(false);
            fetchAuthorities(selectedProfile);
        } catch (e) { alert("Failed to add authority"); }
    };

    const handleDelete = async (id) => {
        if (!selectedProfile) return;
        try {
            await axios.delete(`http://127.0.0.1:8000/api/profiles/${selectedProfile}/authorities/${id}`);
            fetchAuthorities(selectedProfile);
        } catch (e) { alert("Failed to delete authority"); }
    };

    return (
        <div className="authorities-view">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                    <h1>Authorities</h1>
                    <p className="text-muted">Manage influential figures for specific profiles.</p>
                </div>

                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
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

                    <button className="btn btn-primary" onClick={() => setIsAdding(!isAdding)} disabled={!selectedProfile}>
                        <Plus size={18} />
                        Add Authority
                    </button>
                </div>
            </div>

            {isAdding && (
                <div className="card" style={{ marginBottom: '2rem' }}>
                    <h3>Add New Authority for {profiles.find(p => p.id === selectedProfile)?.name}</h3>
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

            <div style={{ display: 'grid', gap: '1rem' }}>
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
                        No authorities added for this profile yet.
                    </div>
                )}
            </div>
        </div>
    );
}
