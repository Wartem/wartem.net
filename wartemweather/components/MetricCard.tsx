
import React from 'react';
import { AreaChart, Area, ResponsiveContainer, YAxis } from 'recharts';
import { WeatherDataPoint } from '../types';

interface MetricCardProps {
    title: string;
    value: string | number;
    unit: string;
    data: WeatherDataPoint[];
    dataKey: string;
    color: string;
    icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, data, dataKey, color, icon }) => {
    // Slice data to 24 hours for sparkline
    const sparkData = data.slice(0, 24);

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col justify-between h-40 hover:border-slate-600 transition-colors">
            <div className="flex justify-between items-start">
                <div>
                    <h3 className="text-slate-400 text-xs uppercase tracking-wider font-mono">{title}</h3>
                    <div className="mt-1 flex items-baseline gap-2">
                        <span className="text-2xl font-bold text-white font-mono">{value}</span>
                        <span className="text-sm text-slate-500">{unit}</span>
                    </div>
                </div>
                {icon && <div className="text-slate-600">{icon}</div>}
            </div>
            
            <div className="h-16 w-full -mb-2">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={sparkData}>
                        <defs>
                            <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                                <stop offset="95%" stopColor={color} stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <YAxis domain={['auto', 'auto']} hide />
                        <Area 
                            type="monotone" 
                            dataKey={dataKey} 
                            stroke={color} 
                            strokeWidth={2}
                            fillOpacity={1} 
                            fill={`url(#grad-${dataKey})`} 
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
