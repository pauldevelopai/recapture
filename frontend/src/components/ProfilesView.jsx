import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserPlus, User, AlertTriangle } from 'lucide-react';

export default function ProfilesView() {
    const [profiles, setProfiles] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [newProfile, setNewProfile] = useState({ name: '', age: '', risk_level: 'Low', notes: '' });

    useEffect(() => {
        fetchProfiles();
    }, []);

    const fetchProfiles = async () => {
        try {
            const res = await axios.get('http://127.0.0.1:8000/api/profiles');
            setProfiles(res.data);
        } catch (err) {
            console.error("Error fetching profiles:", err);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://127.0.0.1:8000/api/profiles', newProfile);
            setShowForm(false);
            setNewProfile({ name: '', age: '', risk_level: 'Low', notes: '' });
            fetchProfiles();
        } catch (err) {
            console.error("Error creating profile:", err);
        }
    };

    return (
        <div className="profiles-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1>Profiles</h1>
                    <p className="text-muted">Manage the young people you are protecting.</p>
                </div>
                <button onClick={() => setShowForm(!showForm)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <UserPlus size={18} /> Add Profile
                </button>
            </div>

            {showForm && (
                <div className="card" style={{ marginBottom: '2rem', border: '1px solid var(--primary)' }}>
                    <h3>New Profile</h3>
                    <form onSubmit={handleCreate} style={{ display: 'grid', gap: '1rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <input
                                placeholder="Name"
                                value={newProfile.name}
                                onChange={e => setNewProfile({ ...newProfile, name: e.target.value })}
                                required
                            />
                            <input
                                type="number"
                                placeholder="Age"
                                value={newProfile.age}
                                onChange={e => setNewProfile({ ...newProfile, age: e.target.value })}
                                required
                            />
                        </div>
                        <select
                            value={newProfile.risk_level}
                            onChange={e => setNewProfile({ ...newProfile, risk_level: e.target.value })}
                            style={{ padding: '0.75rem', borderRadius: 'var(--radius)', background: 'var(--surface)', color: 'var(--text)', border: '1px solid var(--border)' }}
                        >
                            <option value="Low">Low Risk</option>
                            <option value="Medium">Medium Risk</option>
                            <option value="High">High Risk</option>
                        </select>
                        <textarea
                            placeholder="Notes / Context"
                            value={newProfile.notes}
                            onChange={e => setNewProfile({ ...newProfile, notes: e.target.value })}
                        />
                        <button type="submit">Save Profile</button>
                    </form>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                {profiles.map(profile => (
                    <div key={profile.id} className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <div style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }}>
                                    <User size={24} />
                                </div>
                                <div>
                                    <h3 style={{ margin: 0 }}>{profile.name}</h3>
                                    <span className="text-muted">{profile.age} years old</span>
                                </div>
                            </div>
                            <span style={{
                                padding: '0.25rem 0.75rem',
                                borderRadius: '1rem',
                                fontSize: '0.875rem',
                                background: profile.risk_level === 'High' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(34, 197, 94, 0.2)',
                                color: profile.risk_level === 'High' ? 'var(--danger)' : 'var(--success)'
                            }}>
                                {profile.risk_level} Risk
                            </span>
                        </div>
                        <p className="text-muted">{profile.notes || "No notes added."}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
