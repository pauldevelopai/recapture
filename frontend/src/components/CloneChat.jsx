import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Send, User, Bot, RefreshCw, TrendingUp, AlertCircle, AlertTriangle } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000/api';

import { useLanguage } from '../context/LanguageContext';

export default function CloneChat() {
    const { id } = useParams(); // subject_id
    const navigate = useNavigate();
    const { language } = useLanguage();

    const [subject, setSubject] = useState(null);
    // ... (rest of state)

    // ... (fetchData and handleTrainClone remain same)

    const handleSendMessage = async (e) => {
        e.preventDefault();

        if (!currentMessage.trim() || !clone) return;

        const userMessage = currentMessage.trim();
        setCurrentMessage('');

        // Add user message to UI immediately
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        }]);

        setSending(true);

        try {
            const response = await axios.post(`${API_URL}/clones/${clone.id}/chat`, {
                clone_id: clone.id,
                message: userMessage,
                language: language // Pass selected language
            });

            // Add clone response
            setMessages(prev => [...prev, {
                role: 'clone',
                content: response.data.clone_response,
                timestamp: new Date().toISOString()
            }]);

            setLastEffectiveness(response.data.effectiveness_score);
            setSuggestions(response.data.suggestions);
            setConversationId(response.data.conversation_id);

        } catch (err) {
            console.error("Error sending message:", err);
            alert("Error communicating with clone.");
        } finally {
            setSending(false);
        }
    };

    const handleNewConversation = () => {
        setMessages([]);
        setConversationId(null);
        setLastEffectiveness(null);
        setSuggestions([]);
    };

    const getEffectivenessColor = (score) => {
        if (score < 20) return 'var(--danger)';
        if (score < 40) return '#ef4444';
        if (score < 60) return 'var(--warning)';
        if (score < 80) return '#22c55e';
        return 'var(--success)';
    };

    const getEffectivenessLabel = (score) => {
        if (score < 20) return 'Counterproductive';
        if (score < 40) return 'Ineffective';
        if (score < 60) return 'Neutral';
        if (score < 80) return 'Somewhat Effective';
        return 'Highly Effective';
    };

    if (loading) {
        return (
            <div className="subjects-page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
                <RefreshCw size={32} style={{ marginBottom: '1rem', animation: 'spin 1s linear infinite' }} />
                <p>Initializing Digital Clone...</p>
                <p className="text-muted" style={{ fontSize: '0.875rem' }}>Analyzing social media posts to build personality model.</p>
                <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
            </div>
        );
    }

    if (clone && clone.status === 'pending') {
        return (
            <div className="subjects-page">
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                    <button onClick={() => navigate(`/subjects/${id}`)} style={{ padding: '0.5rem', minWidth: 'auto' }}>
                        <ArrowLeft size={20} />
                    </button>
                    <div style={{ flex: 1 }}>
                        <h1 style={{ margin: 0 }}>Digital Clone: {subject.name}</h1>
                        <p className="text-muted">Simulation Pending</p>
                    </div>
                </div>

                <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                    <AlertTriangle size={48} style={{ margin: '0 auto 1rem', color: 'var(--warning)' }} />
                    <h2>Clone Not Ready</h2>
                    <p className="text-muted" style={{ maxWidth: '500px', margin: '0 auto 1.5rem' }}>
                        To create a digital clone simulation, we need to analyze the subject's social media posts.
                        Currently, there are no posts available for {subject.name}.
                    </p>
                    <button onClick={() => navigate(`/subjects/${id}`)}>
                        Go to Subject Profile to Add Social Feeds
                    </button>
                </div>
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
                <button onClick={() => navigate(`/subjects/${id}`)} style={{ padding: '0.5rem', minWidth: 'auto' }}>
                    <ArrowLeft size={20} />
                </button>
                <div style={{ flex: 1 }}>
                    <h1 style={{ margin: 0 }}>Digital Clone: {subject.name}</h1>
                    <p className="text-muted">Simulated conversation to test arguments before real-world use</p>
                </div>
                <button onClick={handleNewConversation} style={{ background: 'var(--border)' }}>
                    New Conversation
                </button>
                <button onClick={handleTrainClone} disabled={loading}>
                    <RefreshCw size={16} style={{ marginRight: '0.5rem' }} />
                    Retrain Clone
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '1.5rem', height: 'calc(100vh - 250px)' }}>
                {/* Chat Area */}
                <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                    {/* Messages */}
                    <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
                            {messages.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                                    <Bot size={48} style={{ margin: '0 auto 1rem' }} />
                                    <p>Start a conversation to test your arguments against this digital clone.</p>
                                    <p style={{ fontSize: '0.875rem' }}>This is a simulation based on the subject's personality and beliefs extracted from their social media posts.</p>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    {messages.map((msg, idx) => (
                                        <div
                                            key={idx}
                                            style={{
                                                display: 'flex',
                                                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
                                            }}
                                        >
                                            <div style={{
                                                maxWidth: '70%',
                                                padding: '1rem',
                                                borderRadius: '1rem',
                                                background: msg.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.1)'
                                            }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                                                    <strong>{msg.role === 'user' ? 'You' : subject.name}</strong>
                                                </div>
                                                <p style={{ margin: 0 }}>{msg.content}</p>
                                            </div>
                                        </div>
                                    ))}
                                    <div ref={messagesEndRef} />
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <form onSubmit={handleSendMessage} style={{ borderTop: '1px solid var(--border)', padding: '1rem' }}>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <input
                                    type="text"
                                    value={currentMessage}
                                    onChange={(e) => setCurrentMessage(e.target.value)}
                                    placeholder="Type your argument to test..."
                                    disabled={sending}
                                    style={{ flex: 1 }}
                                />
                                <button type="submit" disabled={sending || !currentMessage.trim()} style={{ minWidth: 'auto', padding: '0.75rem 1.5rem' }}>
                                    <Send size={18} />
                                </button>
                            </div>
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
