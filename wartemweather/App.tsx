
import React, { useState, useEffect, useMemo } from 'react';
import { 
  CloudRain, Wind, Thermometer, Zap, Activity, Settings as SettingsIcon, MapPin, 
  Cpu, ArrowUp, ArrowDown, History, Moon, Sun, Layers, AlertTriangle, Droplets, Tornado,
  Waves, Flower, Sprout, Shirt, Mountain, Heart, Globe, CloudLightning, Eye, Plane, Clock, Timer, Lock
} from 'lucide-react';
import { AppConfig, WeatherDataPoint, WeatherCache, GeminiInsight } from './types';
import { DEFAULT_CONFIG, TRANSLATIONS } from './constants';
import { loadConfig, saveConfig } from './services/storageService';
import { getWeatherData } from './services/weatherService';
import { generateInsight } from './services/geminiService';
import { ComparisonGraph } from './components/WeatherGraph';
import { MetricCard } from './components/MetricCard';
import { Settings } from './components/Settings';
import { WindDirection } from './components/WindDirection';

const MAX_DAILY_AI_REQUESTS = 5;

function App() {
  const [config, setConfig] = useState<AppConfig>(DEFAULT_CONFIG);
  const [data, setData] = useState<WeatherDataPoint[]>([]);
  const [historical, setHistorical] = useState<WeatherDataPoint[]>([]);
  const [elevation, setElevation] = useState(0);
  const [dailyData, setDailyData] = useState<any>(null);
  const [lastUpdated, setLastUpdated] = useState<number>(Date.now());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insight, setInsight] = useState<GeminiInsight | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistorical, setShowHistorical] = useState(false);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiCooldown, setAiCooldown] = useState(0);
  const [aiUsage, setAiUsage] = useState(0);

  // Initialize Config & Usage
  useEffect(() => {
    const loaded = loadConfig();
    setConfig(loaded);
    
    // Load Daily Usage
    const today = new Date().toISOString().split('T')[0];
    const usageKey = `wartem_ai_usage_${today}`;
    const storedUsage = localStorage.getItem(usageKey);
    setAiUsage(storedUsage ? parseInt(storedUsage, 10) : 0);
  }, []);

  // AI Cooldown Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (aiCooldown > 0) {
      interval = setInterval(() => {
        setAiCooldown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [aiCooldown]);

  // Fetch Data with Failsafe Timeout and Cancellation
  useEffect(() => {
    let mounted = true;
    let timeoutId: ReturnType<typeof setTimeout>;
    
    // Create AbortController for this effect run
    const controller = new AbortController();

    const fetch = async () => {
      setLoading(true);
      setError(null);
      
      // Failsafe: Stop loading UI after 15 seconds if API hangs (though Service has its own timeout)
      timeoutId = setTimeout(() => {
        if (mounted) {
          setError("Request timed out. Please check your connection or try again.");
          setLoading(false);
        }
      }, 15000);

      try {
        const location = config.locations.find(l => l.id === config.activeLocationId) || config.locations[0];
        if (!location) throw new Error("Location not found");
        
        const result: WeatherCache = await getWeatherData({
          location,
          models: config.activeModels,
          forceRefresh: false, // Respect cache
          signal: controller.signal // Pass signal to service
        });
        
        if (mounted) {
          setData(result.data || []);
          setElevation(result.elevation || 0);
          setDailyData(result.daily);
          setLastUpdated(result.timestamp); // Set data age
          if (result.historical) setHistorical(result.historical);
          setLoading(false);
          clearTimeout(timeoutId);
        }
      } catch (err: any) {
        if (err.name === 'AbortError') {
            console.log("Fetch aborted");
            return;
        }
        console.error("Fetch error:", err);
        if (mounted) {
          setError(err.message || "Failed to load weather data");
          setLoading(false);
          clearTimeout(timeoutId);
        }
      }
    };

    if (config.activeLocationId && config.locations.length > 0) {
      fetch();
    }
    
    return () => { 
        mounted = false; 
        clearTimeout(timeoutId);
        controller.abort(); // Cancel pending request on unmount/re-run
    };
  }, [config.activeLocationId, config.activeModels]);

  const t = TRANSLATIONS[config.language];
  // Safe check for current data
  const current = data && data.length > 0 ? data[0] : null;
  const activeLoc = config.locations.find(l => l.id === config.activeLocationId);
  
  // Safe temp calculation
  const currentTemp = current ? Number(current[`temperature_2m_${config.activeModels[0]}`] || current.temperature_2m_best_match || current.temperature_2m_smhi_seamless || 0) : 0;

  const handleConfigSave = (newConfig: AppConfig) => {
    setConfig(newConfig);
    saveConfig(newConfig);
  };

  const handleAiAnalysis = async () => {
    if (!current) return;
    
    // Check Daily Limit
    if (aiUsage >= MAX_DAILY_AI_REQUESTS) {
        return; 
    }

    setIsAiLoading(true);
    // Pass the browser-stored key if available
    const result = await generateInsight(current, data, config.language, config.geminiApiKey);
    
    if (result) {
        setInsight(result);
        
        // Update Usage
        const today = new Date().toISOString().split('T')[0];
        const newUsage = aiUsage + 1;
        setAiUsage(newUsage);
        localStorage.setItem(`wartem_ai_usage_${today}`, newUsage.toString());
    }
    
    setIsAiLoading(false);
    setAiCooldown(60); // Start 60s cooldown
  };

  // --- Computed Logic ---

  // Frost Warning
  const showFrostWarning = useMemo(() => {
    if (!current) return false;
    return currentTemp < 1 || (current.soilTemp0cm !== undefined && current.soilTemp0cm < 1);
  }, [current, currentTemp]);

  // Laundry Index
  const getLaundryIndex = () => {
      if (!current) return { label: '-', color: 'text-slate-500' };
      const precip = Number(current.precip || 0);
      const humidity = Number(current.humidity || 0);
      const wind = Number(current.windSpeed || 0);
      const temp = currentTemp;

      if (precip > 0.1 || humidity > 85 || temp < 5) {
          return { label: t.laundryBad, color: 'text-red-400' };
      }
      if (precip === 0 && humidity < 60 && wind > 3 && temp > 15) {
          return { label: t.laundryGood, color: 'text-emerald-400' };
      }
      return { label: t.laundryOk, color: 'text-amber-400' };
  };

  // Pollen Helper
  const getPollenColor = (val: number | undefined) => {
      if (!val || val < 10) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      if (val < 50) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      if (val < 150) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      return 'bg-red-500/20 text-red-400 border-red-500/30';
  };
  const getPollenLevel = (val: number | undefined) => {
      if (!val || val < 10) return t.low;
      if (val < 50) return t.mid;
      if (val < 150) return t.high;
      return 'EXTREM';
  };

  // Sun Cycle Calc
  const getSunCycle = () => {
      if (!dailyData || !dailyData.time || !Array.isArray(dailyData.time)) return null;
      if (!dailyData.sunrise || !Array.isArray(dailyData.sunrise)) return null;
      if (!dailyData.sunset || !Array.isArray(dailyData.sunset)) return null;

      const today = new Date().toISOString().split('T')[0];
      const idx = dailyData.time.findIndex((d: string) => d === today);
      if (idx === -1) return null;
      
      const sunrise = new Date(dailyData.sunrise[idx]);
      const sunset = new Date(dailyData.sunset[idx]);
      const now = new Date();
      
      const format = (d: Date) => d.toLocaleTimeString('sv-SE', {hour: '2-digit', minute:'2-digit'});
      
      const dayLength = sunset.getTime() - sunrise.getTime();
      const elapsed = now.getTime() - sunrise.getTime();
      let pct = Math.max(0, Math.min(100, (elapsed / dayLength) * 100));
      
      if (now < sunrise) pct = 0;
      if (now > sunset) pct = 100;

      return { sunrise: format(sunrise), sunset: format(sunset), pct };
  };

  // CAPE Logic
  const getCapeStatus = (val: number | undefined) => {
      if (val === undefined) return { label: '-', color: 'text-slate-500' };
      if (val < 100) return { label: t.stable, color: 'text-emerald-400' };
      if (val < 1000) return { label: 'Marginellt instabil', color: 'text-yellow-400' };
      if (val < 2500) return { label: t.unstable, color: 'text-orange-400' };
      return { label: t.veryUnstable, color: 'text-red-500' };
  };

  // Visibility Logic
  const getVisibilityStatus = (val: number | undefined) => {
      if (val === undefined) return { label: '-', color: 'text-slate-500' };
      if (val < 1000) return { label: t.fog, color: 'text-red-400' };
      if (val < 5000) return { label: t.haze, color: 'text-orange-400' };
      if (val < 10000) return { label: t.goodVis, color: 'text-yellow-400' };
      return { label: t.clearVis, color: 'text-emerald-400' };
  };

  const sunData = getSunCycle();
  const laundry = getLaundryIndex();
  const capeStatus = getCapeStatus(current?.cape);
  const visibilityStatus = getVisibilityStatus(current?.visibility);
  const isLimitReached = aiUsage >= MAX_DAILY_AI_REQUESTS;

  if (loading && !current) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-cyan-400 font-mono animate-pulse">{t.loading}</div>;

  if (error && !current) return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-red-400 font-mono gap-4">
          <AlertTriangle className="w-12 h-12" />
          <p>{error}</p>
          <button onClick={() => { localStorage.clear(); window.location.reload(); }} className="px-4 py-2 border border-red-400/30 rounded hover:bg-red-400/10 transition">Reset App</button>
      </div>
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-24 selection:bg-cyan-500/30">
      
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-30 px-4 md:px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          {/* Logo Replacement */}
          <img src="/logo.png" alt="WartemWeather Logo" className="w-10 h-10 object-contain drop-shadow-[0_0_8px_rgba(34,211,238,0.2)]" />
          <div className="flex flex-col">
              <h1 className="font-bold text-lg tracking-tight leading-none">WARTEM<span className="font-light text-slate-400">WEATHER</span></h1>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <select 
            value={config.activeLocationId}
            onChange={(e) => handleConfigSave({...config, activeLocationId: e.target.value})}
            className="bg-slate-900 border border-slate-700 text-sm rounded px-3 py-1.5 focus:border-cyan-500 outline-none font-mono max-w-[150px] sm:max-w-xs"
          >
            {config.locations.map(loc => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
          
          <button onClick={() => setShowSettings(true)} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400">
            <SettingsIcon className="w-5 h-5" />
          </button>
        </div>
      </header>

      {/* Frost Warning Banner */}
      {showFrostWarning && (
          <div className="bg-blue-500/10 border-b border-blue-500/20 text-blue-200 px-4 py-2 flex items-center justify-center gap-2 text-sm font-mono animate-pulse">
              <Thermometer className="w-4 h-4 text-blue-400" />
              {t.frostWarning}
          </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 mt-8 max-w-6xl space-y-6">
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column: Categorized Components */}
          <div className="lg:col-span-1 space-y-8">
            
            {/* 1. Main Current Card */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl">
              <div className="flex justify-between items-start">
                <div className="flex flex-col gap-0.5">
                    <span className="text-slate-400 font-mono text-sm uppercase">
                        {new Date().toLocaleDateString('sv-SE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(lastUpdated).toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>
                <span className="bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded text-xs border border-cyan-500/20">LIVE</span>
              </div>
              
              <div className="mt-6 flex flex-col">
                {current && (
                  <>
                  <span className="text-6xl font-bold text-white tracking-tighter">
                    {currentTemp.toFixed(1)}°
                  </span>
                  <div className="text-slate-400 mt-2 flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-slate-200">
                        <MapPin className="w-5 h-5 text-cyan-500" /> 
                        <span className="font-bold text-lg leading-tight">
                            {activeLoc?.name}
                        </span>
                    </div>
                    
                    {/* Expanded Location Details */}
                    <div className="flex flex-col gap-1 ml-7 text-xs font-mono text-slate-500">
                        {(activeLoc?.admin1 || activeLoc?.country) && (
                            <span className="text-slate-400">
                                {[activeLoc?.admin1, activeLoc?.country].filter(Boolean).join(', ')}
                            </span>
                        )}
                        <div className="flex items-center gap-2">
                            <span className="bg-slate-950/50 px-1.5 py-0.5 rounded border border-slate-800/50">
                                {activeLoc?.lat.toFixed(2)}°N, {activeLoc?.lng.toFixed(2)}°E
                            </span>
                            {elevation > 0 && (
                                <span className="text-slate-300">
                                    {elevation} {t.elevation}
                                </span>
                            )}
                        </div>
                    </div>
                  </div>
                  </>
                )}
              </div>

              {/* Sun Cycle Arc */}
              {sunData && (
                  <div className="mt-6 relative h-16 w-full">
                      <div className="absolute inset-x-0 bottom-0 flex justify-between text-xs font-mono text-slate-400">
                          <span>{sunData.sunrise}</span>
                          <span>{sunData.sunset}</span>
                      </div>
                      <svg className="w-full h-12 overflow-visible" viewBox="0 0 100 50" preserveAspectRatio="none">
                          <path d="M5,50 A45,45 0 0,1 95,50" fill="none" stroke="#1e293b" strokeWidth="2" strokeDasharray="4 4" />
                          <path d="M5,50 A45,45 0 0,1 95,50" fill="none" stroke="#fbbf24" strokeWidth="2" strokeDasharray="1000" strokeDashoffset={1000 - (1000 * (sunData.pct / 100)) * (Math.PI * 45 / 100)} pathLength="100" className="transition-all duration-1000" />
                          <circle cx={5 + (90 * (sunData.pct / 100))} cy={50 - Math.sin((sunData.pct / 100) * Math.PI) * 45} r="3" fill="#fbbf24" className="transition-all duration-1000" />
                      </svg>
                  </div>
              )}
            </div>

            {/* AI Button & Result */}
            <div className="space-y-4">
                <button 
                    onClick={handleAiAnalysis}
                    // Disable if loading OR cooldown is active OR (no key in env AND no key in config) OR daily limit reached
                    disabled={isAiLoading || aiCooldown > 0 || isLimitReached || (!process.env.API_KEY && !config.geminiApiKey)}
                    className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-medium transition-all shadow-lg
                        ${(aiCooldown > 0 || isLimitReached) ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700' : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-900/20'}
                        disabled:opacity-80
                    `}
                >
                    {isAiLoading ? (
                        <Cpu className="animate-spin w-5 h-5"/>
                    ) : isLimitReached ? (
                        <Lock className="w-5 h-5" />
                    ) : aiCooldown > 0 ? (
                        <Timer className="w-5 h-5" />
                    ) : (
                        <Cpu className="w-5 h-5"/>
                    )}
                    
                    <div className="flex flex-col items-start leading-none">
                        <span className="text-sm">
                             {isAiLoading ? 'Analyserar...' : 
                             isLimitReached ? t.dailyLimit : 
                             aiCooldown > 0 ? `Vänta ${aiCooldown}s` : 
                             t.aiAnalysis}
                        </span>
                        {!isLimitReached && (
                             <span className="text-[10px] opacity-70 font-mono mt-0.5">
                                 {MAX_DAILY_AI_REQUESTS - aiUsage} {t.usesLeft}
                             </span>
                        )}
                    </div>
                </button>
                
                {insight && (
                    <div className="bg-slate-900 border border-indigo-500/30 p-4 rounded-xl text-sm space-y-3 animate-in fade-in slide-in-from-top-4 duration-500">
                        <div>
                            <span className="text-indigo-400 font-bold block mb-1">Klädsel:</span>
                            <p className="text-slate-300">{insight.clothing}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                            <div className="bg-slate-950 p-2 rounded">
                                <span className="text-emerald-400 font-bold block text-xs">TRÄDGÅRD</span>
                                <p className="text-slate-400 text-xs mt-1">{insight.activities.gardening}</p>
                            </div>
                            <div className="bg-slate-950 p-2 rounded">
                                <span className="text-cyan-400 font-bold block text-xs">SEGLING</span>
                                <p className="text-slate-400 text-xs mt-1">{insight.activities.sailing}</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* CATEGORY: METRICS (MÄTVÄRDEN) */}
            <div className="space-y-3">
               <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex items-center gap-2">
                   {t.metrics} <span className="text-slate-500 text-xs font-normal normal-case">{t.metricsSubtitle}</span>
               </h2>
               <div className="grid grid-cols-2 gap-3">
                    {/* Row 1 */}
                    <MetricCard 
                        title={t.wind} 
                        value={Number(current?.windSpeed).toFixed(1)} 
                        unit="m/s" 
                        data={data} 
                        dataKey="windSpeed" 
                        color="#22d3ee" 
                    />
                    <MetricCard 
                        title={t.gusts} 
                        value={Number(current?.windGusts).toFixed(1)} 
                        unit="m/s" 
                        data={data} 
                        dataKey="windGusts" 
                        color="#f472b6" 
                    />
                    
                    {/* Row 2 */}
                    <MetricCard 
                        title={t.humidity} 
                        value={Math.round(Number(current?.humidity || 0))} 
                        unit="%" 
                        data={data} 
                        dataKey="humidity" 
                        color="#38bdf8" 
                    />
                    <WindDirection degrees={current?.windDirection || 0} title={t.windDirection || 'Vindriktning'} lang={config.language} />
                    
                    {/* Row 3 - Full Width */}
                    <div className="col-span-2">
                        <MetricCard 
                            title={t.precipitation} 
                            value={Number(current?.precip).toFixed(1)} 
                            unit="mm" 
                            data={data} 
                            dataKey="precip" 
                            color="#60a5fa" 
                        />
                    </div>
               </div>
            </div>

            {/* CATEGORY: CLOUDS (MOLNIGHET) */}
             <div className="space-y-3">
                <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex gap-2 items-center">
                    <Layers className="w-4 h-4 text-slate-400" />
                    {t.clouds}
                </h2>
                <div className="grid grid-cols-3 gap-3 h-32">
                     {/* Low */}
                     <div className="bg-slate-900 border border-slate-800 rounded-lg relative overflow-hidden group hover:border-slate-600 transition-colors">
                         <div className="absolute inset-x-0 bottom-0 bg-slate-800/80 transition-all duration-1000" style={{height: `${current?.cloudLow}%`}}></div>
                         <div className="relative z-10 p-3 h-full flex flex-col justify-between">
                             <span className="text-[10px] uppercase tracking-wider font-mono text-slate-400 font-bold">{t.low}</span>
                             <div className="text-right"><span className="text-2xl font-bold font-mono text-white">{current?.cloudLow}%</span></div>
                         </div>
                     </div>
                     {/* Mid */}
                     <div className="bg-slate-900 border border-slate-800 rounded-lg relative overflow-hidden group hover:border-slate-600 transition-colors">
                         <div className="absolute inset-x-0 bottom-0 bg-slate-700/80 transition-all duration-1000" style={{height: `${current?.cloudMid}%`}}></div>
                         <div className="relative z-10 p-3 h-full flex flex-col justify-between">
                             <span className="text-[10px] uppercase tracking-wider font-mono text-slate-400 font-bold">{t.mid}</span>
                             <div className="text-right"><span className="text-2xl font-bold font-mono text-white">{current?.cloudMid}%</span></div>
                         </div>
                     </div>
                     {/* High */}
                     <div className="bg-slate-900 border border-slate-800 rounded-lg relative overflow-hidden group hover:border-slate-600 transition-colors">
                         <div className="absolute inset-x-0 bottom-0 bg-slate-600/80 transition-all duration-1000" style={{height: `${current?.cloudHigh}%`}}></div>
                         <div className="relative z-10 p-3 h-full flex flex-col justify-between">
                             <span className="text-[10px] uppercase tracking-wider font-mono text-slate-400 font-bold">{t.high}</span>
                             <div className="text-right"><span className="text-2xl font-bold font-mono text-white">{current?.cloudHigh}%</span></div>
                         </div>
                     </div>
                </div>
             </div>

             {/* CATEGORY: COAST & MARINE (KUST & HAV) */}
             {current?.waveHeight !== undefined && (
                <div className="space-y-3">
                    <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex items-center gap-2">
                        <Waves className="w-4 h-4 text-cyan-400" />
                        {t.coast}
                    </h2>
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 grid grid-cols-2 gap-4">
                        <div className="bg-slate-950 p-3 rounded border border-slate-800/50">
                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">{t.waves}</div>
                            <div className="text-2xl text-white font-mono">{current.waveHeight}m</div>
                        </div>
                        <div className="bg-slate-950 p-3 rounded border border-slate-800/50">
                            <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">{t.waveDir}</div>
                            <div className="flex items-center gap-2">
                                <div className="text-2xl text-white font-mono">{current.waveDirection}°</div>
                                <ArrowUp className="w-4 h-4 text-slate-500" style={{transform: `rotate(${current.waveDirection}deg)`}} />
                            </div>
                        </div>
                    </div>
                </div>
             )}

             {/* CATEGORY: NATURE & BIOLOGY (NATUR & BIOLOGI) */}
             <div className="space-y-3">
                 <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex items-center gap-2">
                     <Flower className="w-4 h-4 text-emerald-400" />
                     {t.nature}
                 </h2>
                 
                 <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                     {/* Pollen List */}
                     <div className="space-y-3">
                          <div className="text-xs text-slate-400 uppercase font-mono font-bold">{t.pollen}</div>
                          <div className="space-y-2">
                              <div className="flex justify-between items-center text-xs border-b border-slate-800/50 pb-2">
                                  <span className="text-slate-400">{t.birch}</span>
                                  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${getPollenColor(current?.pollenBirch)}`}>{getPollenLevel(current?.pollenBirch)}</span>
                              </div>
                              <div className="flex justify-between items-center text-xs border-b border-slate-800/50 pb-2">
                                  <span className="text-slate-400">{t.grass}</span>
                                  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${getPollenColor(current?.pollenGrass)}`}>{getPollenLevel(current?.pollenGrass)}</span>
                              </div>
                              <div className="flex justify-between items-center text-xs">
                                  <span className="text-slate-400">{t.mugwort}</span>
                                  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${getPollenColor(current?.pollenMugwort)}`}>{getPollenLevel(current?.pollenMugwort)}</span>
                              </div>
                          </div>
                     </div>

                     <div className="grid grid-cols-2 gap-8 pt-2 border-t border-slate-800">
                          <div>
                              <div className="text-[10px] text-slate-500 uppercase font-bold">{t.gardening}</div>
                              <div className={`font-mono text-xl font-bold mt-1 ${Number(current?.soilTemp0cm) < 0 ? 'text-blue-400' : 'text-emerald-400'}`}>
                                  {current?.soilTemp0cm !== undefined ? `${current.soilTemp0cm}°` : '-'}
                              </div>
                          </div>
                          <div>
                              <div className="text-[10px] text-slate-500 uppercase font-bold">{t.aqi}</div>
                              <div className="font-mono text-xl font-bold text-white mt-1">
                                  {current?.aqi !== undefined ? Math.round(current.aqi) : '-'}
                              </div>
                          </div>
                     </div>
                 </div>
             </div>

            {/* CATEGORY: LIFESTYLE & HEALTH (LIVSSTIL & HÄLSA) */}
             <div className="space-y-3">
                <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex gap-2 items-center">
                    <Heart className="w-4 h-4 text-rose-400" />
                    {t.lifestyle}
                </h2>
                <div className="grid grid-cols-2 gap-4">
                    {/* Laundry */}
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col items-center justify-center text-center gap-2 h-32">
                        <Shirt className={`w-6 h-6 ${laundry.color}`} />
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase font-bold font-mono">{t.laundry}</div>
                            <div className={`text-sm font-bold ${laundry.color}`}>{laundry.label}</div>
                        </div>
                    </div>
                    {/* UV Index */}
                    <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-col items-center justify-center text-center gap-2 relative overflow-hidden h-32">
                        {current?.uvIndex !== undefined && current.uvIndex > 3 && (
                            <div className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full animate-pulse m-2"></div>
                        )}
                        <Sun className="w-6 h-6 text-orange-400" />
                        <div>
                            <div className="text-[10px] text-slate-500 uppercase font-bold font-mono">{t.uvIndex}</div>
                            <div className="text-2xl font-bold text-white">
                                {current?.uvIndex !== undefined ? Number(current.uvIndex).toFixed(1) : '-'}
                            </div>
                        </div>
                    </div>
                </div>
             </div>

             {/* CATEGORY: THUNDER & INSTABILITY (ÅSKA & INSTABILITET) */}
             <div className="space-y-3">
                 <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex items-center gap-2">
                    <CloudLightning className="w-4 h-4 text-yellow-400" />
                    {t.cape}
                 </h2>
                 <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
                     <div className="flex justify-between items-center mb-3">
                         <div>
                             <div className="text-[10px] text-slate-500 uppercase font-bold font-mono">{t.capeLabel}</div>
                             <div className="text-3xl font-bold font-mono text-white tracking-tight">{Math.round(current?.cape || 0)}</div>
                         </div>
                         <div className={`text-xs font-bold px-3 py-1.5 rounded bg-slate-950 border border-slate-800 ${capeStatus.color}`}>
                             {capeStatus.label}
                         </div>
                     </div>
                     {/* Simple Bar Gauge */}
                     <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                         <div className="h-full bg-gradient-to-r from-emerald-500 via-yellow-500 to-red-500 transition-all duration-1000" style={{width: `${Math.min(100, ((current?.cape || 0) / 2000) * 100)}%`}}></div>
                     </div>
                 </div>
             </div>

             {/* CATEGORY: VISIBILITY & AVIATION (SIKT & FLYG) - Expanded */}
             <div className="space-y-3">
                 <h2 className="text-slate-300 font-mono text-sm uppercase font-bold flex gap-2 items-center">
                    <Eye className="w-4 h-4 text-cyan-400" />
                    {t.visibility}
                 </h2>
                 <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex flex-col justify-between h-40">
                     <div className="flex justify-between items-start">
                         <div className="flex flex-col gap-1">
                             <div className="text-4xl font-bold font-mono text-white">
                                 {current?.visibility !== undefined ? (current.visibility / 1000).toFixed(1) : '-'}
                                 <span className="text-xl font-normal text-slate-500 ml-1">km</span>
                             </div>
                             <div className={`text-sm font-bold ${visibilityStatus.color}`}>
                                 {visibilityStatus.label}
                             </div>
                         </div>
                         <div className="bg-slate-950 px-3 py-2 rounded border border-slate-800 text-right">
                             <div className="flex items-center gap-1 text-[10px] text-slate-500 uppercase font-bold justify-end">
                                 <Plane className="w-3 h-3" />
                                 {t.aviation}
                             </div>
                             <div className="text-xs font-bold text-slate-300 mt-1">
                                 {(current?.visibility || 0) > 8000 && (current?.cloudLow || 0) < 50 ? 'VFR (Visual Flight Rules)' : 'IFR (Instrument Flight Rules)'}
                             </div>
                         </div>
                     </div>
                     {/* Visibility Progress Bar */}
                     <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-4">
                         <div className="bg-cyan-500 h-full transition-all duration-1000" style={{width: `${Math.min(100, ((current?.visibility || 0) / 10000) * 100)}%`}}></div>
                     </div>
                 </div>
             </div>

          </div>

          {/* Right Column: Graphs */}
          <div className="lg:col-span-2 flex flex-col gap-6">
             
             {/* 1. Graphs */}
             <div className="flex justify-between items-center">
                 <h2 className="text-slate-300 font-mono text-sm uppercase flex items-center gap-2">
                    <Activity className="w-4 h-4 text-slate-500" />
                    {t.models}
                 </h2>
                 <button 
                    onClick={() => setShowHistorical(!showHistorical)}
                    className={`text-xs px-3 py-1 border rounded-full flex items-center gap-2 transition-all ${showHistorical ? 'bg-amber-500/20 border-amber-500 text-amber-500' : 'border-slate-700 text-slate-500'}`}
                 >
                    <History className="w-3 h-3" />
                    {t.timeMachine}
                 </button>
             </div>
             
             {data.length > 0 && (
                <div className="space-y-6">
                    <ComparisonGraph 
                        title={t.comparisonTemp}
                        type="temp"
                        data={data} 
                        historicalData={historical} 
                        activeModels={config.activeModels}
                        showHistorical={showHistorical}
                    />
                    <ComparisonGraph 
                        title={t.comparisonWind}
                        type="wind"
                        data={data} 
                        historicalData={historical}
                        activeModels={config.activeModels}
                        showHistorical={showHistorical}
                    />
                    <ComparisonGraph 
                        title={t.comparisonRain}
                        type="rain"
                        data={data} 
                        historicalData={historical}
                        activeModels={config.activeModels}
                        showHistorical={showHistorical}
                    />
                    <ComparisonGraph 
                        title={t.pressure}
                        type="temp" // Reuse graph style
                        data={data.map(d => ({...d, temperature_2m_best_match: d.pressure}))} // Hack mapping for reuse
                        activeModels={['best_match' as any]} // Only show pressure line
                        showHistorical={false}
                    />
                </div>
             )}
          </div>

        </div>

      </main>

      <footer className="py-8 text-center text-slate-500 text-xs font-mono border-t border-slate-800/50 mt-12">
        <p>
          WartemWeather stores preferences & API keys locally in your browser. No personal data is collected.
        </p>
      </footer>

      {showSettings && (
        <Settings 
            config={config} 
            onSave={handleConfigSave} 
            onClose={() => setShowSettings(false)}
            labels={t}
        />
      )}
    </div>
  );
}

export default App;
