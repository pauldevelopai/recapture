import { useState, useEffect } from 'react';
import axios from 'axios';
import { UserPlus, User, AlertTriangle } from 'lucide-react';

export default function SubjectsView() {
    const [subjects, setSubjects] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [newSubject, setNewSubject] = useState({ name: '', age: '', risk_level: 'Low', notes: '' });

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
            await axios.post('http://127.0.0.1:8000/api/subjects', newSubject);
            setShowForm(false);
            setNewSubject({ name: '', age: '', risk_level: 'Low', notes: '' });
            fetchSubjects();
        } catch (err) {
            console.error("Error creating subject:", err);
        }
    };

    return (
        <div className="subjects-page">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h1>Subjects</h1>
                    <p className="text-muted">Manage the young people (Digital Clones) you are protecting.</p>
                </div>
                <button onClick={() => setShowForm(!showForm)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <UserPlus size={18} /> Add Subject
                </button>
            </div>

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
                        <button type="submit">Save Subject</button>
                    </form>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                {subjects.map(subject => (
                    <div key={subject.id} className="card">
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
        </div>
    );
}
