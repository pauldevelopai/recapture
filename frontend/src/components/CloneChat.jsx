import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Send, User, Bot, ArrowLeft, RefreshCw, AlertCircle, MessageSquare, Brain, Sparkles } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const API_URL = 'http://127.0.0.1:8000/api';

export default function CloneChat() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { language } = useLanguage();
    const [subject, setSubject] = useState(null);
    const [clone, setClone] = useState(null);
    const [loading, setLoading] = useState(true);
    const [userMessage, setUserMessage] = useState('');
    const [messages, setMessages] = useState([]);
    const [sending, setSending] = useState(false);
    const [lastEffectiveness, setLastEffectiveness] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [subjectRes, cloneRes] = await Promise.all([
                    axios.get(`${API_URL}/subjects/${id}`),
                    axios.get(`${API_URL}/clones/${id}`)
                ]);
                setSubject(subjectRes.data);
                setClone(cloneRes.data);

                // Fetch conversation history
                try {
                    const convRes = await axios.get(`${API_URL}/clones/${cloneRes.data.id}/conversations`);
                    if (convRes.data && convRes.data.length > 0) {
                        // Load last conversation
                        const lastConv = convRes.data[0];
                        setMessages(lastConv.conversation);
                        setLastEffectiveness(lastConv.effectiveness_score);
                    }
                } catch (e) {
                    console.log("No previous conversations found");
                }

            } catch (err) {
                console.error("Error fetching clone data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!userMessage.trim() || !clone) return;

        const newMessage = { role: 'user', content: userMessage, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, newMessage]);
        setUserMessage('');
        setSending(true);

        try {
            const response = await axios.post(`${API_URL}/clones/${clone.id}/chat`, {
                clone_id: clone.id,
                message: userMessage,
                language: language // Pass selected language
            });

            const cloneReply = {
                role: 'clone',
                content: response.data.clone_response,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, cloneReply]);
            setLastEffectiveness(response.data.effectiveness_score);
            setSuggestions(response.data.suggestions || []);

        } catch (err) {
            console.error("Error sending message:", err);
            alert("Error communicating with clone.");
        } finally {
            setSending(false);
        }
    };

    const getEffectivenessColor = (score) => {
        if (score < 20) return 'var(--danger)';
        if (score < 40) return 'var(--warning)';
        if (score < 60) return 'var(--text-muted)';
        if (score < 80) return 'var(--primary)';
        return 'var(--success)';
    };

    const getEffectivenessLabel = (score) => {
        if (score < 20) return 'Counterproductive';
        if (score < 40) return 'Ineffective';
        if (score < 60) return 'Neutral';
        if (score < 80) return 'Effective';
        return 'Highly Effective';
    };

    if (loading) {
        return (
            <div className="subjects-page" style={{ justifyContent: 'center', alignItems: 'center' }}>
                <div className="spinner"></div>
            </div>
        );
    }

    if (!subject || !clone) {
        return (
            <div className="subjects-page">
                <p>Unable to load digital clone. Make sure social media posts have been scraped.</p>
                <button onClick={() => navigate(`/subjects/${id}`)}>Back to Subject</button>
            </div>
        );
    }

    return (
        <div className="subjects-page">
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                <button
                    onClick={() => navigate(`/subjects/${id}`)}
                    style={{ background: 'none', border: 'none', color: 'var(--text)', cursor: 'pointer', padding: 0 }}
                >
                    <ArrowLeft size={24} />
                </button>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Brain size={24} color="var(--primary)" />
                        <h1>Digital Clone: {subject.name}</h1>
                    </div>
                    <p className="text-muted">Simulate a conversation to test arguments and strategies.</p>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '2rem', height: 'calc(100vh - 200px)' }}>
                {/* Chat Area */}
                <div className="card" style={{ display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
                    <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {messages.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                <Sparkles size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
                                <p>Start a conversation to see how {subject.name} responds.</p>
                                <p style={{ fontSize: '0.875rem' }}>The clone will respond based on their personality and beliefs.</p>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} style={{
                                display: 'flex',
                                gap: '1rem',
                                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                                alignItems: 'flex-start'
                            }}>
                                <div style={{
                                    width: '32px', height: '32px',
                                    borderRadius: '50%',
                                    background: msg.role === 'user' ? 'var(--primary)' : 'var(--secondary)',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    flexShrink: 0
                                }}>
                                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                                </div>
                                <div style={{
                                    maxWidth: '70%',
                                    padding: '1rem',
                                    borderRadius: '1rem',
                                    background: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                                    color: 'white',
                                    borderTopRightRadius: msg.role === 'user' ? '0' : '1rem',
                                    borderTopLeftRadius: msg.role === 'clone' ? '0' : '1rem'
                                }}>
                                    <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                                    <div style={{ fontSize: '0.7rem', opacity: 0.7, marginTop: '0.5rem', textAlign: 'right' }}>
                                        {new Date(msg.timestamp).toLocaleTimeString()}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    <div style={{ padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.2)' }}>
                        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '1rem' }}>
                            <input
                                type="text"
                                value={userMessage}
                                onChange={(e) => setUserMessage(e.target.value)}
                                placeholder={`Message ${subject.name}...`}
                                style={{ flex: 1 }}
                                disabled={sending}
                            />
                            <button type="submit" disabled={sending || !userMessage.trim()} className="primary">
                                {sending ? <RefreshCw className="spin" size={20} /> : <Send size={20} />}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Sidebar */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', overflowY: 'auto' }}>
                    {/* Clone Info */}
                    <div className="card">
                        <h3>Clone Status</h3>
                        <div style={{ display: 'grid', gap: '0.75rem', fontSize: '0.875rem' }}>
                            <div>
                                <strong>Status:</strong>
                                <span style={{
                                    marginLeft: '0.5rem',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '1rem',
                                    background: clone.status === 'ready' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(251, 191, 36, 0.2)',
                                    color: clone.status === 'ready' ? 'var(--success)' : 'var(--warning)'
                                }}>
                                    {clone.status}
                                </span>
                            </div>
                            <div>
                                <strong>Training Posts:</strong> {clone.training_post_count}
                            </div>
                            {clone.last_trained && (
                                <div>
                                    <strong>Last Trained:</strong>
                                    <br />
                                    {new Date(clone.last_trained).toLocaleString()}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Personality Summary */}
                    {clone.personality_model && Object.keys(clone.personality_model).length > 0 && (
                        <div className="card">
                            <h3>Personality Profile</h3>
                            <div style={{ display: 'grid', gap: '0.75rem', fontSize: '0.875rem' }}>
                                {clone.personality_model.traits && clone.personality_model.traits.length > 0 && (
                                    <div>
                                        <strong>Traits:</strong>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.5rem' }}>
                                            {clone.personality_model.traits.slice(0, 5).map((trait, idx) => (
                                                <span key={idx} style={{
                                                    padding: '0.25rem 0.5rem',
                                                    background: 'rgba(255,255,255,0.1)',
                                                    borderRadius: '0.25rem',
                                                    fontSize: '0.75rem'
                                                }}>
                                                    {trait}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {clone.personality_model.communication_style && (
                                    <div>
                                        <strong>Communication Style:</strong>
                                        <p className="text-muted" style={{ margin: '0.25rem 0 0 0' }}>
                                            {clone.personality_model.communication_style}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Effectiveness Score */}
                    {lastEffectiveness !== null && (
                        <div className="card">
                            <h3>Argument Effectiveness</h3>
                            <div style={{ textAlign: 'center', padding: '1rem' }}>
                                <div style={{
                                    fontSize: '3rem',
                                    fontWeight: 'bold',
                                    color: getEffectivenessColor(lastEffectiveness)
                                }}>
                                    {Math.round(lastEffectiveness)}
                                </div>
                                <p style={{ color: getEffectivenessColor(lastEffectiveness), margin: '0.5rem 0 0 0' }}>
                                    {getEffectivenessLabel(lastEffectiveness)}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Suggestions */}
                    {suggestions.length > 0 && (
                        <div className="card">
                            <h3>Improvement Suggestions</h3>
                            <div style={{ display: 'grid', gap: '0.75rem' }}>
                                {suggestions.map((suggestion, idx) => (
                                    <div key={idx} style={{
                                        padding: '0.75rem',
                                        background: 'rgba(255,255,255,0.05)',
                                        borderRadius: '0.5rem',
                                        fontSize: '0.875rem',
                                        borderLeft: '3px solid var(--primary)'
                                    }}>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '0.1rem' }} />
                                            <span>{suggestion}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Interests */}
                    {clone.interests && clone.interests.length > 0 && (
                        <div className="card">
                            <h3>Interests</h3>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                {clone.interests.slice(0, 8).map((interest, idx) => (
                                    <span key={idx} style={{
                                        padding: '0.25rem 0.5rem',
                                        background: 'rgba(255,255,255,0.1)',
                                        borderRadius: '0.25rem',
                                        fontSize: '0.75rem'
                                    }}>
                                        {interest}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
