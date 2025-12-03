import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Radio, Pause, Play, RefreshCw, ExternalLink } from 'lucide-react';

const ListeningFeed = () => {
    const [isListening, setIsListening] = useState(false);
    const [feed, setFeed] = useState([]);
    const [stats, setStats] = useState({ total: 0, threats: 0 });
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const itemsPerPage = 5;
    const feedEndRef = useRef(null);

    // Poll for updates when listening
    useEffect(() => {
        fetchFeed(currentPage);
        checkStatus();

        let interval;
        if (isListening) {
            interval = setInterval(() => fetchFeed(currentPage, true), 3000); // Silent refresh
        }
        return () => clearInterval(interval);
    }, [isListening, currentPage]);

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

    const startListening = async () => {
        try {
            await fetch('http://localhost:8000/api/listening/start', { method: 'POST' });
            setIsListening(true);
            fetchFeed(1); // Reset to first page on start
            setCurrentPage(1);
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

    const fetchFeed = async (page, silent = false) => {
        if (!silent) setIsLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/api/listening/feed?page=${page}&page_size=${itemsPerPage}`);
            const data = await response.json();

            setFeed(data.items);
            setStats({ total: data.total, threats: 0 }); // Threats count would need a separate endpoint for total stats
            setTotalPages(data.total_pages);
        } catch (error) {
            console.error("Failed to fetch feed:", error);
        } finally {
            if (!silent) setIsLoading(false);
        }
    };

    const getSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'critical': return 'text-red-500 border-red-500/50 bg-red-500/10';
            case 'high': return 'text-orange-500 border-orange-500/50 bg-orange-500/10';
            case 'medium': return 'text-yellow-500 border-yellow-500/50 bg-yellow-500/10';
            default: return 'text-gray-400 border-gray-700 bg-gray-800/50';
        }
    };

    const feedAreaRef = useRef(null);

    // Scroll to top when page changes
    useEffect(() => {
        if (feedAreaRef.current) {
            feedAreaRef.current.scrollTop = 0;
        }
    }, [currentPage]);

    return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden flex flex-col h-[600px]">
            {/* Header */}
            <div className="p-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/50 backdrop-blur-sm flex-none">
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
                            <span className="text-gray-500 text-xs">Total Scanned</span>
                            <span className="text-white font-mono">{stats.total}</span>
                        </div>
                    </div>

                    <button
                        onClick={() => fetchFeed(currentPage)}
                        className="p-2 rounded-lg bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white transition-colors"
                        title="Refresh Feed"
                    >
                        <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    </button>

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
            <div ref={feedAreaRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar relative">
                {isLoading && (
                    <div className="absolute inset-0 bg-gray-900/50 flex items-center justify-center z-10 backdrop-blur-sm">
                        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
                    </div>
                )}

                {feed.length === 0 && !isLoading ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-3">
                        <Radio className="w-12 h-12 opacity-20" />
                        <p>No activity detected. Start listening to monitor channels.</p>
                    </div>
                ) : (
                    feed.map((item) => (
                        <div
                            key={item.id}
                            className={`p-5 rounded-xl border transition-all duration-300 shadow-sm hover:shadow-md ${item.matched_trend_id
                                ? 'bg-gray-800 border-red-500/30 hover:border-red-500/50'
                                : 'bg-gray-800 border-gray-700 hover:border-gray-600'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <span className={`text-[10px] font-bold px-2 py-1 rounded-md border uppercase tracking-wider ${item.source_platform === '4chan' ? 'bg-green-900/20 text-green-400 border-green-500/30' :
                                        item.source_platform === 'reddit' ? 'bg-orange-900/20 text-orange-400 border-orange-500/30' :
                                            'bg-gray-700 text-gray-300 border-gray-600'
                                        }`}>
                                        {item.source_platform}
                                    </span>
                                    <div className="flex flex-col">
                                        <span className="text-sm font-semibold text-gray-200">@{item.author}</span>
                                        <span className="text-xs text-gray-500">{new Date(item.timestamp).toLocaleString()}</span>
                                    </div>
                                </div>
                                {item.matched_trend_id && (
                                    <span className={`text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1.5 uppercase tracking-wider ${getSeverityColor(item.severity)}`}>
                                        <AlertTriangle className="w-3 h-3" />
                                        {item.severity} Risk
                                    </span>
                                )}
                            </div>

                            <p className="text-gray-300 text-sm leading-relaxed mb-4 font-normal whitespace-pre-wrap">
                                {item.content}
                            </p>

                            <div className="flex items-center justify-between pt-4 border-t border-gray-700/50">
                                <div className="flex items-center gap-4">
                                    {item.matched_trend_topic && (
                                        <span className="text-xs text-red-400 font-medium flex items-center gap-1.5 bg-red-500/5 px-2 py-1 rounded">
                                            <Shield className="w-3 h-3" />
                                            {item.matched_trend_topic}
                                        </span>
                                    )}
                                    {item.url && (
                                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1.5 hover:underline">
                                            <ExternalLink className="w-3 h-3" /> Source Link
                                        </a>
                                    )}
                                </div>
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
                                    className="text-xs bg-blue-600 text-white border border-blue-500 px-4 py-2 rounded-lg hover:bg-blue-500 transition-all shadow-sm hover:shadow flex items-center gap-2 font-medium"
                                >
                                    <Shield className="w-3.5 h-3.5" /> Promote to Intel
                                </button>
                            </div>
                        </div>
                    ))
                )}
                <div ref={feedEndRef} />
            </div>

            {/* Pagination Footer */}
            <div className="p-4 border-t border-gray-700 bg-gray-800 flex justify-center items-center gap-6 flex-none">
                <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1 || isLoading}
                    className="px-4 py-2 text-sm font-medium bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-gray-600 flex items-center gap-2"
                >
                    &larr; Previous
                </button>

                <span className="text-sm text-gray-300 font-medium bg-gray-900 px-3 py-1 rounded border border-gray-700">
                    Page {currentPage} of {totalPages || 1}
                </span>

                <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage >= totalPages || isLoading}
                    className="px-4 py-2 text-sm font-medium bg-gray-700 text-white rounded hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-gray-600 flex items-center gap-2"
                >
                    Next &rarr;
                </button>
            </div>
        </div>
    );
};

export default ListeningFeed;
