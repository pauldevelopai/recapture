import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useLanguage } from '../context/LanguageContext';

const API_URL = 'http://127.0.0.1:8000/api';

export default function CloneChat() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { language } = useLanguage();
    const [subject, setSubject] = useState(null);
    const [clone, setClone] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                console.log("Fetching data for:", id);
                const [subjectRes, cloneRes] = await Promise.all([
                    axios.get(`${API_URL}/subjects/${id}`),
                    axios.get(`${API_URL}/clones/${id}`)
                ]);
                console.log("Data fetched:", subjectRes.data, cloneRes.data);
                setSubject(subjectRes.data);
                setClone(cloneRes.data);
            } catch (err) {
                console.error("Error fetching data:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    if (loading) return <div style={{ padding: '2rem' }}>Loading...</div>;
    if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;
    if (!subject || !clone) return <div style={{ padding: '2rem' }}>Unable to load data.</div>;

    return (
        <div style={{ padding: '2rem', color: 'white' }}>
            <h1>Digital Clone: {subject.name}</h1>
            <div style={{ marginTop: '1rem', padding: '1rem', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
                <p><strong>Status:</strong> {clone.status}</p>
                <p><strong>Training Posts:</strong> {clone.training_post_count}</p>
                <p><strong>Personality:</strong> {clone.personality_model?.communication_style || 'N/A'}</p>
            </div>

            <div style={{ marginTop: '2rem' }}>
                <h3>Chat Interface (Simplified)</h3>
                <p>The full chat interface is currently under maintenance. Please check back later.</p>
                <button
                    onClick={() => navigate(`/subjects/${id}`)}
                    style={{ marginTop: '1rem', padding: '0.5rem 1rem', cursor: 'pointer' }}
                >
                    Back to Subject
                </button>
            </div>
        </div>
    );
}
