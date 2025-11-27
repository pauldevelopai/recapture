import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Globe, Users, Activity, AlertTriangle, ShieldAlert, Zap, MapPin } from 'lucide-react';

export default function BotFarmMonitor() {
    const [farms, setFarms] = useState([]);
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
            const [farmsRes, campaignsRes] = await Promise.all([
                axios.get('http://127.0.0.1:8000/api/bot-farms'),
                axios.get('http://127.0.0.1:8000/api/campaigns')
            ]);
            setFarms(farmsRes.data);
            setCampaigns(campaignsRes.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch bot farm data:", err);
        }
    };

    const handleSimulate = async () => {
        try {
            await axios.post('http://127.0.0.1:8000/api/campaigns/simulate');
            fetchData();
        } catch (err) {
            console.error("Simulation failed:", err);
        }
    };

    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'active': return 'var(--danger)';
            case 'dormant': return 'var(--text-muted)';
            case 'suspended': return 'var(--success)';
            default: return 'var(--primary)';
        }
    };

    return (
        <div className="bot-farm-monitor">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2>Bot Farm & Campaign Monitor</h2>
                    <p className="text-muted">Real-time tracking of organized disinformation networks.</p>
                </div>
                <button onClick={handleSimulate} className="btn btn-primary">
                    <Zap size={16} style={{ marginRight: '0.5rem' }} /> Simulate Activity
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
                {/* Global Stats */}
                <div className="card">
                    <h3><Globe size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Active Networks</h3>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--danger)', margin: '1rem 0' }}>
                        {farms.filter(f => f.status === 'Active').length}
                    </div>
                    <div className="text-muted">Total Bot Farms Monitored: {farms.length}</div>
                </div>
                <div className="card">
                    <h3><Activity size={20} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Active Campaigns</h3>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--warning)', margin: '1rem 0' }}>
                        {campaigns.filter(c => c.status === 'Active').length}
                    </div>
                    <div className="text-muted">Targeting {campaigns.reduce((acc, c) => acc + c.reach_estimate, 0).toLocaleString()} users</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Bot Farms List */}
                <div>
                    <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <ShieldAlert size={20} /> Known Bot Farms
                    </h3>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {farms.map(farm => (
                            <div key={farm.id} className="card" style={{ borderLeft: `4px solid ${getStatusColor(farm.status)}` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                    <div>
                                        <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{farm.name}</h4>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                            <MapPin size={14} /> {farm.origin_country}
                                        </div>
                                    </div>
                                    <span style={{
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '1rem',
                                        fontSize: '0.8rem',
                                        background: 'rgba(255,255,255,0.1)',
                                        color: getStatusColor(farm.status),
                                        fontWeight: 'bold'
                                    }}>
                                        {farm.status.toUpperCase()}
                                    </span>
                                </div>
                                <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', fontSize: '0.9rem' }}>
                                    <div>
                                        <strong>Size:</strong> {farm.network_size.toLocaleString()} bots
                                    </div>
                                    <div>
                                        <strong>Tactics:</strong> {farm.primary_tactics.join(', ')}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Active Campaigns List */}
                <div>
                    <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <AlertTriangle size={20} /> Active Campaigns
                    </h3>
                    <div style={{ display: 'grid', gap: '1rem' }}>
                        {campaigns.map(campaign => (
                            <div key={campaign.id} className="card" style={{ background: 'rgba(255,255,255,0.03)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                    <h4 style={{ margin: 0 }}>{campaign.name}</h4>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--warning)' }}>{campaign.status}</span>
                                </div>
                                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                    Goal: {campaign.narrative_goal}
                                </p>
                                <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.75rem', borderRadius: '6px', fontSize: '0.9rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                        <span>Target: {campaign.target_demographic}</span>
                                        <span>Reach: <strong>{campaign.reach_estimate.toLocaleString()}</strong></span>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        {campaign.active_platforms.map(p => (
                                            <span key={p} style={{ background: 'var(--surface)', padding: '0.1rem 0.5rem', borderRadius: '4px', fontSize: '0.8rem' }}>
                                                {p}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
