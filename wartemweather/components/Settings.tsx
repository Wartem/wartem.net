
import React, { useState } from 'react';
import { AppConfig, Location, WeatherModel, Language } from '../types';
import { MODEL_LABELS, MODEL_COLORS } from '../constants';
import { searchLocations } from '../services/weatherService';
import { Search, MapPin, Loader2, Plus, Check, Key, ShieldCheck } from 'lucide-react';

interface SettingsProps {
    config: AppConfig;
    onSave: (newConfig: AppConfig) => void;
    onClose: () => void;
    labels: any;
}

export const Settings: React.FC<SettingsProps> = ({ config, onSave, onClose, labels }) => {
    const [activeTab, setActiveTab] = useState<'general' | 'json'>('general');
    const [jsonText, setJsonText] = useState(JSON.stringify(config, null, 2));
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<Location[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [apiKey, setApiKey] = useState(config.geminiApiKey || '');

    // Check if a system key exists in the environment (e.g. injected by Vercel/Netlify or Dev Env)
    const hasSystemKey = typeof process !== 'undefined' && process.env && !!process.env.API_KEY;

    const handleSaveJson = () => {
        try {
            const parsed = JSON.parse(jsonText);
            if (!parsed.locations || !parsed.activeModels) {
                throw new Error("Invalid config schema");
            }
            onSave(parsed);
            onClose();
        } catch (e: any) {
            setError(e.message);
        }
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        setIsSearching(true);
        const results = await searchLocations(searchQuery);
        setSearchResults(results);
        setIsSearching(false);
    };

    const addLocation = (loc: Location) => {
        const newConfig = {
            ...config,
            locations: [...config.locations, loc],
            activeLocationId: loc.id
        };
        onSave(newConfig);
        setJsonText(JSON.stringify(newConfig, null, 2));
        onClose();
    };

    const toggleModel = (model: WeatherModel) => {
        const current = config.activeModels;
        const next = current.includes(model) 
            ? current.filter(m => m !== model)
            : [...current, model];
            
        if (next.length === 0) return; // Prevent disabling all models
        
        const newConfig = { ...config, activeModels: next };
        onSave(newConfig);
        setJsonText(JSON.stringify(newConfig, null, 2));
    };

    const changeLanguage = (lang: Language) => {
        const newConfig = { ...config, language: lang };
        onSave(newConfig);
        setJsonText(JSON.stringify(newConfig, null, 2));
    };

    const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setApiKey(val);
        const newConfig = { ...config, geminiApiKey: val };
        onSave(newConfig);
        setJsonText(JSON.stringify(newConfig, null, 2));
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-lg w-full max-w-2xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
                <h2 className="text-xl text-white font-mono mb-4">{labels.settings}</h2>
                
                <div className="flex gap-4 mb-6 border-b border-slate-800">
                    <button 
                        onClick={() => setActiveTab('general')}
                        className={`pb-2 text-sm font-mono transition-colors ${activeTab === 'general' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400'}`}
                    >
                        {labels.dashboard}
                    </button>
                    <button 
                        onClick={() => setActiveTab('json')}
                        className={`pb-2 text-sm font-mono transition-colors ${activeTab === 'json' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400'}`}
                    >
                        JSON Config
                    </button>
                </div>

                {activeTab === 'general' && (
                    <div className="space-y-8">
                         {/* Language Selection */}
                         <div>
                            <h3 className="text-sm font-mono text-slate-400 mb-3 uppercase tracking-wider">{labels.language}</h3>
                            <div className="flex gap-2 flex-wrap">
                                {Object.values(Language).map((lang) => (
                                     <button
                                        key={lang}
                                        onClick={() => changeLanguage(lang)}
                                        className={`px-3 py-1 rounded text-sm font-mono border transition-colors uppercase ${
                                            config.language === lang 
                                            ? 'bg-cyan-900/30 border-cyan-500 text-cyan-400' 
                                            : 'bg-slate-900 border-slate-700 text-slate-500 hover:border-slate-500'
                                        }`}
                                     >
                                        {lang}
                                     </button>
                                ))}
                            </div>
                         </div>

                         {/* API Key Section */}
                         <div>
                            <h3 className="text-sm font-mono text-slate-400 mb-3 uppercase tracking-wider">{labels.apiKeyLabel}</h3>
                            <div className="bg-slate-950 p-4 rounded border border-slate-800">
                                <div className="flex gap-2 items-center mb-2">
                                    <Key className="w-4 h-4 text-cyan-400" />
                                    <span className="text-xs text-slate-500">{labels.apiKeyDesc}</span>
                                </div>
                                
                                {hasSystemKey && !apiKey && (
                                    <div className="mb-3 flex items-center gap-2 text-xs text-emerald-400 bg-emerald-400/10 px-3 py-2 rounded border border-emerald-400/20">
                                        <ShieldCheck className="w-4 h-4" />
                                        <span>System Key Active. Users do not need to enter a key.</span>
                                    </div>
                                )}

                                <input 
                                    type="password"
                                    value={apiKey}
                                    onChange={handleApiKeyChange}
                                    placeholder={hasSystemKey ? "Optional (System Key in use)" : "Enter Gemini API Key..."}
                                    className="w-full bg-slate-900 border border-slate-700 text-white p-2 rounded focus:border-cyan-500 focus:outline-none font-mono text-sm placeholder:text-slate-600"
                                />
                            </div>
                         </div>

                         {/* Location Search */}
                         <div>
                             <h3 className="text-sm font-mono text-slate-400 mb-3 uppercase tracking-wider">{labels.addLocation}</h3>
                             <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <input 
                                        type="text" 
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                        placeholder={labels.searchLocationPlaceholder}
                                        className="w-full bg-slate-950 border border-slate-800 text-white p-2 pl-9 rounded focus:border-cyan-500 focus:outline-none font-mono text-sm"
                                    />
                                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                                </div>
                                <button 
                                    onClick={handleSearch}
                                    disabled={isSearching}
                                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded font-mono text-sm border border-slate-700 transition-colors"
                                >
                                    {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : labels.search}
                                </button>
                             </div>

                             <div className="space-y-2 mt-4">
                                {searchResults.map((loc) => (
                                    <button 
                                        key={loc.id}
                                        onClick={() => addLocation(loc)}
                                        className="w-full flex items-center justify-between p-3 bg-slate-950/50 hover:bg-cyan-900/10 border border-slate-800 hover:border-cyan-500/30 rounded group transition-all"
                                    >
                                        <div className="flex items-center gap-3">
                                            <MapPin className="w-4 h-4 text-slate-500 group-hover:text-cyan-400" />
                                            <div className="text-left">
                                                <div className="text-slate-200 font-medium text-sm">{loc.name}</div>
                                                <div className="text-slate-500 text-xs">
                                                    {[loc.admin1, loc.country].filter(Boolean).join(', ')}
                                                </div>
                                            </div>
                                        </div>
                                        <Plus className="w-4 h-4 text-slate-600 group-hover:text-cyan-400" />
                                    </button>
                                ))}
                             </div>
                         </div>

                         {/* Model Selection */}
                         <div>
                            <h3 className="text-sm font-mono text-slate-400 mb-3 uppercase tracking-wider">{labels.models}</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {Object.values(WeatherModel).map((model) => (
                                    <button
                                        key={model}
                                        onClick={() => toggleModel(model)}
                                        className={`flex items-center justify-between p-3 rounded border transition-all text-sm font-mono
                                            ${config.activeModels.includes(model) 
                                                ? 'bg-slate-800/80 border-cyan-500/50 text-cyan-50' 
                                                : 'bg-slate-950/50 border-slate-800 text-slate-500 hover:border-slate-600'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <span 
                                                className="w-3 h-3 rounded-full shadow-sm" 
                                                style={{backgroundColor: config.activeModels.includes(model) ? MODEL_COLORS[model] : '#334155'}}
                                            />
                                            {MODEL_LABELS[model]}
                                        </div>
                                        {config.activeModels.includes(model) && <Check className="w-4 h-4 text-cyan-400" />}
                                    </button>
                                ))}
                            </div>
                         </div>
                    </div>
                )}

                {activeTab === 'json' && (
                    <>
                        <p className="text-slate-400 text-sm mb-4">
                            Modify locations, active models, or language directly. 
                        </p>
                        <textarea 
                            className="w-full h-64 bg-slate-950 border border-slate-800 text-green-400 font-mono text-sm p-4 rounded focus:outline-none focus:border-cyan-500"
                            value={jsonText}
                            onChange={(e) => setJsonText(e.target.value)}
                        />
                        {error && <p className="text-red-400 text-xs mt-2 font-mono">Error: {error}</p>}
                    </>
                )}

                <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-slate-800">
                    <button 
                        onClick={onClose}
                        className="px-4 py-2 rounded text-slate-300 hover:text-white font-mono text-sm"
                    >
                        {labels.cancel}
                    </button>
                    {activeTab === 'json' && (
                        <button 
                            onClick={handleSaveJson}
                            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-sm shadow-lg shadow-cyan-900/20"
                        >
                            {labels.save}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
