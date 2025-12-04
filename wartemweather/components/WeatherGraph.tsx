import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, Label } from 'recharts';
import { WeatherDataPoint, WeatherModel } from '../types';
import { MODEL_COLORS, MODEL_LABELS } from '../constants';

interface ComparisonGraphProps {
    data: WeatherDataPoint[];
    historicalData?: WeatherDataPoint[]; // 1 year ago
    activeModels: WeatherModel[];
    showHistorical?: boolean;
    type: 'temp' | 'wind' | 'rain';
    title: string;
}

const formatTime = (iso: string) => {
    const d = new Date(iso);
    return `${d.getHours()}:00`;
};

// Simplified tooltip that handles dynamic keys based on type
const CustomTooltip = ({ active, payload, label, type }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-slate-950 border border-slate-700 p-3 rounded shadow-xl text-xs font-mono z-50">
                <p className="text-slate-400 mb-2 border-b border-slate-800 pb-1">{new Date(label).toLocaleString('sv-SE')}</p>
                {payload.map((entry: any) => (
                    <div key={entry.name} className="flex justify-between gap-4 mb-1">
                        <span style={{ color: entry.color }}>
                            {entry.name === 'historical' ? '1 År Sedan' : entry.name}:
                        </span>
                        <span className="text-white font-bold">
                            {Number(entry.value).toFixed(1)}
                            {type === 'temp' ? '°' : type === 'wind' ? ' m/s' : ' mm'}
                        </span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

export const ComparisonGraph: React.FC<ComparisonGraphProps> = ({ data, historicalData, activeModels, showHistorical, type, title }) => {
    
    // Determine closest data point to "Now" for the marker
    const closestTime = useMemo(() => {
        if (!data || data.length === 0) return null;
        const now = Date.now();
        let minDiff = Infinity;
        let bestTime = null;

        for (const point of data) {
            const t = new Date(point.time).getTime();
            const diff = Math.abs(t - now);
            if (diff < minDiff) {
                minDiff = diff;
                bestTime = point.time;
            }
        }
        return bestTime;
    }, [data]);

    // Determine data keys based on type
    const getKey = (model: string) => {
        if (type === 'temp') return `temperature_2m_${model}`;
        if (type === 'wind') return `wind_speed_10m_${model}`;
        if (type === 'rain') return `precipitation_${model}`;
        return '';
    };

    // Determine historical key based on type
    const getHistoricalKey = () => {
        if (type === 'temp') return 'temp_historical';
        if (type === 'wind') return 'wind_historical';
        if (type === 'rain') return 'precip_historical';
        return undefined;
    };

    const histKey = getHistoricalKey();

    const chartData = data.map((point, i) => {
        const d: any = { ...point };
        if (showHistorical && historicalData && historicalData[i] && histKey) {
            d.historical = historicalData[i][histKey];
        }
        return d;
    });

    return (
        <div className="w-full h-[400px] bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col">
            <h3 className="text-slate-400 text-xs uppercase tracking-wider font-mono mb-4 flex-shrink-0">
                {title}
            </h3>
            <div className="flex-grow min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                        <XAxis 
                            dataKey="time" 
                            tickFormatter={formatTime} 
                            stroke="#475569" 
                            tick={{ fontSize: 12, fontFamily: 'JetBrains Mono' }} 
                            minTickGap={30}
                        />
                        <YAxis 
                            stroke="#475569" 
                            tick={{ fontSize: 12, fontFamily: 'JetBrains Mono' }} 
                            domain={['auto', 'auto']}
                        />
                        <Tooltip content={(props) => <CustomTooltip {...props} type={type} />} />
                        
                        {/* Reference Line for Current Time */}
                        {closestTime && (
                            <ReferenceLine x={closestTime} stroke="#f43f5e" strokeDasharray="3 3">
                                <Label value="Nu" position="insideTop" fill="#f43f5e" fontSize={10} fontFamily="JetBrains Mono" />
                            </ReferenceLine>
                        )}

                        {/* Render active models */}
                        {activeModels.map((model) => (
                            <Line
                                key={model}
                                type="monotone"
                                dataKey={getKey(model)}
                                name={MODEL_LABELS[model]} // Use nice name for Legend
                                stroke={MODEL_COLORS[model]}
                                strokeWidth={2}
                                dot={false}
                                activeDot={{ r: 5 }}
                                connectNulls
                            />
                        ))}

                        {/* Render Time Machine Line */}
                        {showHistorical && histKey && (
                            <Line
                                type="monotone"
                                dataKey="historical"
                                name="historical"
                                stroke="#ffffff"
                                strokeWidth={1}
                                strokeDasharray="5 5"
                                dot={false}
                                opacity={0.5}
                            />
                        )}
                    </LineChart>
                </ResponsiveContainer>
            </div>
            
            {/* Custom Legend Outside the Chart */}
            <div className="mt-4 flex flex-wrap gap-4 justify-center border-t border-slate-800/50 pt-2 flex-shrink-0">
                 {activeModels.map(model => (
                     <div key={model} className="flex items-center gap-2 text-xs font-mono text-slate-300">
                         <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: MODEL_COLORS[model] }}></span>
                         {MODEL_LABELS[model]}
                     </div>
                 ))}
                 {showHistorical && (
                     <div className="flex items-center gap-2 text-xs font-mono text-slate-300 opacity-75">
                         <span className="w-2.5 h-2.5 rounded-full border border-white bg-transparent"></span>
                         1 År Sedan
                     </div>
                 )}
            </div>
        </div>
    );
};