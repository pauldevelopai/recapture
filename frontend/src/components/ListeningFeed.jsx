import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Radio, Pause, Play, RefreshCw, ExternalLink } from 'lucide-react';

const ListeningFeed = () => {
    const [isListening, setIsListening] = useState(false);
    const [feed, setFeed] = useState([]);
    const [stats, setStats] = useState({ total: 0, threats: 0 });
    const feedEndRef = useRef(null);

    // Poll for updates when listening
    useEffect(() => {
        fetchFeed(); // Fetch immediately on mount to show history
        checkStatus(); // Sync status with backend

        let interval;
        if (isListening) {
            interval = setInterval(fetchFeed, 2000);
        }
        return () => clearInterval(interval);
    }, [isListening]);

    const checkStatus = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/listening/status');
            const data = await response.json();
            if (data.running && !isListening) {
                setIsListening(true);
            }
        } catch (error) {
            console.error("Failed to check status:", error);
        }
    };

    // Auto-scroll to top when new items arrive (if we were doing a chat style, but for a feed usually top is newest)
    // For this feed, we'll put newest at the top, so no auto-scroll needed.

    const startListening = async () => {
        try {
            await fetch('http://localhost:8000/api/listening/start', { method: 'POST' });
            setIsListening(true);
            fetchFeed(); // Immediate fetch
        } catch (error) {
            console.error("Failed to start listening:", error);
        }
    };

    const stopListening = async () => {
        try {
            await fetch('http://localhost:8000/api/listening/stop', { method: 'POST' });
            setIsListening(false);
        } catch (error) {
            console.error("Failed to stop listening:", error);
        }
    };

    const fetchFeed = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/listening/feed');
            const data = await response.json();

            setFeed(prevFeed => {
                // Create a map of existing IDs for fast lookup
                const existingIds = new Set(prevFeed.map(item => item.id));

                // Filter out items that are already in the feed
                const newItems = data.filter(item => !existingIds.has(item.id));

                if (newItems.length === 0) return prevFeed;

                // Combine and sort by timestamp (newest first)
                const combined = [...newItems, ...prevFeed].sort((a, b) =>
                    new Date(b.timestamp) - new Date(a.timestamp)
                );

                return combined;
            });

            // Update stats based on the latest fetch (total in DB vs total in view is tricky, 
            // but let's show stats for what's in view or just use the latest fetch stats if backend provided them.
            // For now, let's calculate stats based on the *merged* feed in the next render, 
            // or just update it here based on the data we just fetched if we want "latest scan" stats.
            // Actually, let's update stats based on the *new* combined list. 
            // Since setFeed is async, we can't do it right here easily without repeating logic.
            // Let's just update stats based on the incoming batch for "Scanned" count, 
            // or better, use a useEffect on 'feed' to update stats.
        } catch (error) {
            console.error("Failed to fetch feed:", error);
        }
    };

    // Update stats whenever feed changes
    useEffect(() => {
        const threatCount = feed.filter(item => item.matched_trend_id).length;
        setStats({ total: feed.length, threats: threatCount });
    }, [feed]);

    const getSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return 'text-red-500 border-red-500/50 bg-red-500/10';
            case 'high': return 'text-orange-500 border-orange-500/50 bg-orange-500/10';
            case 'medium': return 'text-yellow-500 border-yellow-500/50 bg-yellow-500/10';
            default: return 'text-gray-400 border-gray-700 bg-gray-800/50';
        }
    };

    return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden flex flex-col h-[600px]">
            {/* Header */}
            <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50 backdrop-blur-sm">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${isListening ? 'bg-green-500/20 text-green-400 animate-pulse' : 'bg-gray-800 text-gray-400'}`}>
                        <Radio className="w-5 h-5" />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">Deep Listening Feed</h3>
                        <p className="text-xs text-gray-400">
                            {isListening ? 'Monitoring active channels...' : 'Monitoring paused'}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <div className="flex gap-4 mr-4 text-sm">
                        <div className="flex flex-col items-end">
                            <span className="text-gray-500 text-xs">Scanned</span>
                            <span className="text-white font-mono">{stats.total}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-red-500/70 text-xs">Threats</span>
                            <span className="text-red-400 font-mono">{stats.threats}</span>
                        </div>
                    </div>

                    <button
                        onClick={isListening ? stopListening : startListening}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${isListening
                            ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/50'
                            : 'bg-green-500/10 text-green-400 hover:bg-green-500/20 border border-green-500/50'
                            }`}
                    >
                        {isListening ? (
                            <>
                                <Pause className="w-4 h-4" /> Stop
                            </>
                        ) : (
                            <>
                                <Play className="w-4 h-4" /> Start Listening
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Feed Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {feed.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-3">
                        <Radio className="w-12 h-12 opacity-20" />
                        <p>No activity detected. Start listening to monitor channels.</p>
                    </div>
                ) : (
                    feed.map((item) => (
                        <div
                            key={item.id}
                            className={`p-4 rounded-lg border transition-all duration-300 ${item.matched_trend_id
                                ? 'bg-red-900/10 border-red-500/30 hover:border-red-500/50'
                                : 'bg-gray-800/30 border-gray-700/50 hover:border-gray-600'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                                        {item.source_platform}
                                    </span>
                                    <span className="text-sm text-gray-400">@{item.author}</span>
                                    <span className="text-xs text-gray-600">• {new Date(item.timestamp).toLocaleTimeString()}</span>
                                    {item.url && (
                                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                                            <ExternalLink className="w-3 h-3" /> View
                                        </a>
                                    )}
                                </div>
                                {item.matched_trend_id && (
                                    <span className={`text-xs font-bold px-2 py-0.5 rounded flex items-center gap-1 ${getSeverityColor(item.severity)}`}>
                                        <AlertTriangle className="w-3 h-3" />
                                        {item.severity.toUpperCase()} THREAT
                                    </span>
                                )}
                            </div>

                            <p className="text-gray-200 text-sm leading-relaxed mb-2">
                                {item.content}
                            </p>

                            <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-700/50">
                                {item.matched_trend_topic && (
                                    <span className="text-xs text-red-400 font-medium">
                                        Detected Theme: {item.matched_trend_topic}
                                    </span>
                                )}
                                <button
                                    onClick={async () => {
                                        try {
                                            await fetch('http://localhost:8000/api/listening/promote', {
                                                method: 'POST',
                                                headers: { 'Content-Type': 'application/json' },
                                                body: JSON.stringify(item)
                                            });
                                            alert("Sent to Training Queue!");
                                        } catch (e) {
                                            console.error(e);
                                            alert("Failed to send to training.");
                                        }
                                    }}
                                    className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/30 px-2 py-1 rounded hover:bg-blue-500/20 transition-colors flex items-center gap-1"
                                >
                                    <Shield className="w-3 h-3" /> Send to Training
                                </button>
                            </div>
                        </div>
                    ))
                )}
                <div ref={feedEndRef} />
            </div>
        </div>
    );
};

export default ListeningFeed;
