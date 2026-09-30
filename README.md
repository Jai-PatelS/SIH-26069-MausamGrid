# SIH-26069-MausamGrid
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MausamGrid - SIH 26069 Command Center</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        body { 
            margin: 0; padding: 0; 
            font-family: 'Space Grotesk', sans-serif; 
            background: radial-gradient(circle at center, #f8fafc 0%, #e2e8f0 100%); 
            color: #1e293b; 
            overflow-x: hidden; 
        }
        
        .font-mono { font-family: 'JetBrains Mono', monospace; }

        #weather-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; opacity: 0.15; }
        
        .glass-panel { 
            background: rgba(255, 255, 255, 0.85); 
            backdrop-filter: blur(20px); 
            border: 1px solid rgba(14, 165, 233, 0.2); 
            box-shadow: 0 20px 40px rgba(148, 163, 184, 0.25), inset 0 0 15px rgba(255, 255, 255, 0.5);
            border-radius: 16px; 
            z-index: 10; 
        }

        #map { width: 100%; height: 500px; border-radius: 12px; background: #e2e8f0; }
        
        /* Clean Daylight Map Style */
        .leaflet-tile {
            filter: contrast(1.05) saturate(0.9);
        }

        .leaflet-popup-content-wrapper { 
            background: rgba(255, 255, 255, 0.95); 
            backdrop-filter: blur(10px);
            color: #1e293b; 
            border: 1px solid #0ea5e9; 
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(14, 165, 233, 0.15);
        }
        .leaflet-popup-tip { background: #ffffff; }

        .neon-btn { 
            background: rgba(14, 165, 233, 0.05); 
            border: 1px solid rgba(14, 165, 233, 0.3); 
            color: #0284c7; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
        }
        .neon-btn:hover, .neon-btn.active { 
            background: #0ea5e9; 
            color: white; 
            border-color: #0284c7;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.4); 
        }

        /* Live Ticker Animation */
        .ticker-wrap { width: 100%; overflow: hidden; white-space: nowrap; background: rgba(14, 165, 233, 0.08); border-top: 1px solid rgba(14, 165, 233, 0.2); border-bottom: 1px solid rgba(14, 165, 233, 0.2); padding: 6px 0; }
        .ticker { display: inline-block; animation: ticker 35s linear infinite; }
        .ticker-item { display: inline-block; padding: 0 2rem; font-size: 11px; font-family: 'JetBrains Mono', monospace; color: #0369a1; text-transform: uppercase; font-weight: 600; }
        @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-50%, 0, 0); } }

        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; flex-grow: 1; }
        .layout-wrapper { position: relative; z-index: 10; width: 100%; min-height: 100vh; display: flex; flex-direction: column; box-sizing: border-box; }

        @keyframes pulse-glow { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.05); } }
        .pulse-badge { animation: pulse-glow 2s infinite; }
    </style>
</head>
<body>

    <canvas id="weather-canvas"></canvas>

    <div class="layout-wrapper">
        
        <!-- Top Command Header -->
        <header class="glass-panel p-5 mx-5 mt-5 mb-3 flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-sky-500 to-cyan-400 flex items-center justify-center shadow-[0_0_20px_rgba(14,165,233,0.4)]">
                    <i class="fa-solid fa-satellite-dish text-xl text-white"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-widest uppercase text-slate-800">Mausam<span class="text-sky-600">Grid</span></h1>
                    <p class="text-[10px] text-sky-700 tracking-widest uppercase font-mono font-bold">SIH PS-26069 | National Big Data Analytics Platform</p>
                </div>
            </div>

            <div class="flex flex-wrap gap-2">
                <button onclick="switchTab('telemetry')" id="nav-telemetry" class="neon-btn active px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider"><i class="fa-solid fa-map-location-dot mr-1"></i> Live Map</button>
                <button onclick="switchTab('emergency')" id="nav-emergency" class="neon-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider"><i class="fa-solid fa-phone-volume text-rose-600 mr-1"></i> Emergency Hub</button>
                <button onclick="switchTab('analytics')" id="nav-analytics" class="neon-btn px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider"><i class="fa-solid fa-chart-pie mr-1"></i> Engine Analytics</button>
            </div>
            
            <div class="hidden lg:flex items-center gap-3 bg-white px-4 py-2 rounded-xl border border-slate-200 shadow-sm">
                <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-badge shadow-[0_0_8px_#10b981]"></div>
                <div class="text-right">
                    <p class="text-[10px] text-slate-400 uppercase tracking-widest font-mono">FastAPI Core</p>
                    <p class="text-emerald-600 font-bold text-xs font-mono">ONLINE & SYNCED</p>
                </div>
            </div>
        </header>

        <!-- Live Status Ticker Bar -->
        <div class="ticker-wrap mb-4">
            <div class="ticker">
                <span class="ticker-item"><i class="fa-solid fa-shield-halved text-sky-600 mr-1"></i> AI Verification Pipeline: Active</span>
                <span class="ticker-item"><i class="fa-solid fa-triangle-exclamation text-amber-600 mr-1"></i> WMO Standard Telemetry Stream Connected</span>
                <span class="ticker-item"><i class="fa-solid fa-server text-emerald-600 mr-1"></i> Node Latency: 24ms</span>
                <span class="ticker-item"><i class="fa-solid fa-database text-purple-600 mr-1"></i> Open-Meteo Bulk Stream: Synchronized</span>
                <span class="ticker-item"><i class="fa-solid fa-shield-halved text-sky-600 mr-1"></i> AI Verification Pipeline: Active</span>
                <span class="ticker-item"><i class="fa-solid fa-triangle-exclamation text-amber-600 mr-1"></i> WMO Standard Telemetry Stream Connected</span>
                <span class="ticker-item"><i class="fa-solid fa-server text-emerald-600 mr-1"></i> Node Latency: 24ms</span>
                <span class="ticker-item"><i class="fa-solid fa-database text-purple-600 mr-1"></i> Open-Meteo Bulk Stream: Synchronized</span>
            </div>
        </div>

        <div class="px-5 pb-5 flex flex-col flex-grow">
            <!-- TAB 1: LIVE MAP -->
            <div id="tab-telemetry" class="tab-content active gap-6">
                <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-grow">
                    <div class="glass-panel p-5 lg:col-span-3 flex flex-col">
                        <div class="flex flex-col md:flex-row justify-between items-center mb-4 gap-3">
                            <div class="flex items-center gap-2">
                                <div class="w-2 h-2 rounded-full bg-sky-500 animate-ping"></div>
                                <h2 class="text-xs font-bold uppercase tracking-widest text-slate-700 font-mono">National Live Telemetry Grid</h2>
                            </div>
                            <div class="flex flex-wrap gap-2">
                                <button onclick="fetchData()" id="btn-all" class="neon-btn active px-3.5 py-1.5 rounded-lg text-xs font-bold uppercase">All Signals</button>
                                <button onclick="fetchData('Heavy Rainfall', null)" id="btn-rain" class="neon-btn px-3.5 py-1.5 rounded-lg text-xs font-bold uppercase">Rainfall Only</button>
                                <button onclick="fetchData(null, true)" id="btn-verified" class="neon-btn px-3.5 py-1.5 rounded-lg text-xs font-bold uppercase">AI Verified Only</button>
                            </div>
                        </div>
                        <div id="map" class="flex-grow shadow-inner border border-slate-200"></div>
                    </div>

                    <!-- Telemetry Summary Sidebar -->
                    <div class="glass-panel p-6 flex flex-col gap-6 justify-between">
                        <div>
                            <h2 class="text-xs font-bold uppercase tracking-wider text-sky-700 border-b border-slate-200 pb-3 mb-5 font-mono"><i class="fa-solid fa-chart-line mr-2"></i>Telemetry Summary</h2>
                            
                            <div class="space-y-4">
                                <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1 font-mono">Total Signals Intercepted</p>
                                    <p class="text-3xl font-bold text-slate-800 font-mono" id="stat-total">0</p>
                                </div>
                                <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1 font-mono">AI Verified Signals</p>
                                    <p class="text-3xl font-bold text-emerald-600 font-mono" id="stat-verified">0</p>
                                </div>
                                <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1 font-mono">Pending / Flagged</p>
                                    <p class="text-3xl font-bold text-rose-600 font-mono" id="stat-pending">0</p>
                                </div>
                                <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                    <p class="text-[10px] text-slate-500 uppercase tracking-widest mb-1 font-mono">Mean Confidence Score</p>
                                    <p class="text-2xl font-bold text-sky-600 font-mono" id="stat-confidence">0%</p>
                                </div>
                            </div>
                        </div>

                        <div class="bg-sky-50 p-4 rounded-xl border border-sky-200">
                            <h3 class="text-[11px] font-bold text-sky-800 uppercase mb-1 font-mono"><i class="fa-solid fa-microchip mr-1"></i> AI Verification Pipeline</h3>
                            <p class="text-[11px] text-slate-600 leading-relaxed">Cross-referencing live meteorological telemetry with automated threat classification algorithms.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: EMERGENCY HUB -->
            <div id="tab-emergency" class="tab-content gap-6">
                <div class="glass-panel p-8 flex flex-col">
                    <div class="mb-6">
                        <h2 class="text-lg font-bold uppercase tracking-widest text-rose-600 font-mono"><i class="fa-solid fa-triangle-exclamation mr-2"></i> National Disaster Emergency Hotlines</h2>
                        <p class="text-xs text-slate-600 mt-1 font-mono">Quick-access verified response contacts for state authorities and emergency relief units.</p>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:border-sky-400 transition-all">
                            <div class="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold mb-4"><i class="fa-solid fa-shield-halved text-lg"></i></div>
                            <h3 class="font-bold text-sm text-slate-800 mb-1">NDRF Control Room</h3>
                            <p class="text-[11px] text-slate-500 mb-4">National Disaster Response Force</p>
                            <p class="text-xl font-mono font-bold text-sky-600 mb-3">1078 / 011-24363260</p>
                            <span class="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-lg uppercase tracking-wider font-mono">24/7 Active Line</span>
                        </div>
                        <div class="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:border-sky-400 transition-all">
                            <div class="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center font-bold mb-4"><i class="fa-solid fa-cloud-bolt text-lg"></i></div>
                            <h3 class="font-bold text-sm text-slate-800 mb-1">IMD Weather Helpline</h3>
                            <p class="text-[11px] text-slate-500 mb-4">Indian Meteorological Department</p>
                            <p class="text-xl font-mono font-bold text-sky-600 mb-3">011-24651346</p>
                            <span class="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-lg uppercase tracking-wider font-mono">Verified Portal</span>
                        </div>
                        <div class="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm hover:border-sky-400 transition-all">
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold mb-4"><i class="fa-solid fa-phone-volume text-lg"></i></div>
                            <h3 class="font-bold text-sm text-slate-800 mb-1">Emergency SOS Line</h3>
                            <p class="text-[11px] text-slate-500 mb-4">Pan-India Unified Helpline</p>
                            <p class="text-xl font-mono font-bold text-sky-600 mb-3">112</p>
                            <span class="px-2.5 py-1 bg-emerald-50 text-emerald-600 text-[10px] font-bold rounded-lg uppercase tracking-wider font-mono">All-in-One Emergency</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 3: BACKEND ANALYTICS -->
            <div id="tab-analytics" class="tab-content gap-6">
                <div class="glass-panel p-8 flex flex-col">
                    <h2 class="text-lg font-bold uppercase tracking-widest text-sky-700 mb-2 font-mono"><i class="fa-solid fa-server mr-2"></i>FastAPI Processing Engine Metrics</h2>
                    <p class="text-xs text-slate-600 mb-6 font-mono">Live architectural status from python runtime environment.</p>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h3 class="text-sm font-bold text-slate-800 uppercase mb-3 font-mono"><i class="fa-solid fa-microchip text-sky-600 mr-2"></i> Server Framework & Routing</h3>
                            <p class="text-xs text-slate-600 leading-relaxed">Built with FastAPI and asynchronous Uvicorn routing. Incoming payloads undergo strict Pydantic model validation before being parsed against live Open-Meteo telemetry databases.</p>
                        </div>
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                            <h3 class="text-sm font-bold text-slate-800 uppercase mb-3 font-mono"><i class="fa-solid fa-shield-virus text-rose-600 mr-2"></i> AI / NLP Verification Logic</h3>
                            <p class="text-xs text-slate-600 leading-relaxed">Computes real-time confidence scores and sentiment assessment based on official WMO weather codes and atmospheric thresholds (e.g., thermal limits exceeding 40°C).</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('header button').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            document.getElementById('nav-' + tabId).classList.add('active');
            if(tabId === 'telemetry') setTimeout(() => { map.invalidateSize(); }, 200);
        }

        const map = L.map('map').setView([20.5937, 78.9629], 5);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        let currentMarkers = [];

        async function fetchStats() {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/stats');
                const stats = await res.json();
                document.getElementById('stat-total').innerText = stats.total_signals;
                document.getElementById('stat-verified').innerText = stats.verified_count;
                document.getElementById('stat-pending').innerText = stats.pending_count;
                document.getElementById('stat-confidence').innerText = stats.avg_confidence + '%';
            } catch (err) {
                console.error("Stats API error. Is uvicorn running?", err);
            }
        }

        async function fetchData(category = null, isVerified = null) {
            document.querySelectorAll('#tab-telemetry .neon-btn').forEach(b => b.classList.remove('active'));
            if(category) document.getElementById('btn-rain').classList.add('active');
            else if(isVerified) document.getElementById('btn-verified').classList.add('active');
            else document.getElementById('btn-all').classList.add('active');

            let url = 'http://127.0.0.1:8000/api/reports?';
            if (category) url += `event_category=${category}&`;
            if (isVerified !== null) url += `is_verified=${isVerified}`;

            try {
                const response = await fetch(url);
                const data = await response.json();
                
                currentMarkers.forEach(marker => map.removeLayer(marker));
                currentMarkers = [];

                data.forEach(report => {
                    let markerColor = report.is_verified ? "#10b981" : "#f43f5e";
                    const customIcon = L.divIcon({
                        className: 'custom-icon',
                        html: `<div style="background-color: ${markerColor}; width: 14px; height: 14px; border-radius: 50%; box-shadow: 0 0 10px ${markerColor}; border: 2px solid white;"></div>`,
                        iconSize: [14, 14]
                    });

                    const marker = L.marker([report.lat, report.lng], {icon: customIcon}).addTo(map);
                    marker.bindPopup(`
                        <div style="font-family: 'Space Grotesk', sans-serif; padding: 4px;">
                            <strong style="font-size: 15px; color: #0284c7;">${report.city}, ${report.state}</strong><br>
                            <span style="color: #475569; font-size: 12px;">Event: ${report.event_category}</span><br>
                            <span style="color: #475569; font-size: 12px;">AI Confidence: ${(report.confidence_score * 100).toFixed(0)}%</span><br>
