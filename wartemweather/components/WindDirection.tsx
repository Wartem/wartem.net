
import React from 'react';
import { Language } from '../types';

interface WindDirectionProps {
    degrees: number;
    title: string;
    lang: Language;
}

export const WindDirection: React.FC<WindDirectionProps> = ({ degrees, title, lang }) => {
    
    const getCardinal = (d: number) => {
        const val = Math.floor((d / 45) + 0.5) % 8;
        const keys = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
        const key = keys[val];

        // Translations
        if (lang === Language.SV || lang === Language.DE) {
            const map: Record<string, string> = {
                'N': 'N', 'NE': 'NO', 'E': 'O', 'SE': 'SO',
                'S': 'S', 'SW': 'SV', 'W': 'V', 'NW': 'NV'
            };
            return map[key] || key;
        }
        
        if (lang === Language.ES || lang === Language.FR) {
             const map: Record<string, string> = {
                'N': 'N', 'NE': 'NE', 'E': 'E', 'SE': 'SE',
                'S': 'S', 'SW': 'SO', 'W': 'O', 'NW': 'NO'
            };
            return map[key] || key;
        }

        return key;
    };

    return (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 flex flex-col justify-between h-40 hover:border-slate-600 transition-colors relative overflow-hidden">
            <h3 className="text-slate-400 text-xs uppercase tracking-wider font-mono z-10">{title}</h3>
            
            <div className="flex flex-col items-center justify-center z-10 flex-1 gap-1 pt-2">
                <span className="text-5xl font-bold text-cyan-400 font-mono tracking-tighter drop-shadow-[0_0_15px_rgba(34,211,238,0.3)]">
                    {getCardinal(degrees)}
                </span>
                <span className="text-sm text-slate-500 font-mono mt-1">
                    {degrees}°
                </span>
            </div>
        </div>
    );
};
