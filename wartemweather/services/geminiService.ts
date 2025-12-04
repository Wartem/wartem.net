
import { GoogleGenAI, Type } from "@google/genai";
import { WeatherDataPoint, GeminiInsight } from "../types";

// Safe access to API Key for browser environments
const getApiKey = (overrideKey?: string) => {
  if (overrideKey) return overrideKey;
  
  try {
    // Check if process is defined before accessing env
    if (typeof process !== 'undefined' && process.env) {
      return process.env.API_KEY;
    }
  } catch (e) {
    // Ignore ReferenceError
  }
  return undefined;
};

const getClient = (overrideKey?: string) => {
    const key = getApiKey(overrideKey);
    if (!key) return null;
    return new GoogleGenAI({ apiKey: key });
};

const getLanguageName = (code: string) => {
    switch(code) {
        case 'sv': return 'Swedish';
        case 'en': return 'English';
        case 'de': return 'German';
        case 'fr': return 'French';
        case 'es': return 'Spanish';
        default: return 'English';
    }
};

export const generateInsight = async (
    currentWeather: WeatherDataPoint, 
    forecast: WeatherDataPoint[], 
    lang: string,
    apiKey?: string
): Promise<GeminiInsight | null> => {
    const ai = getClient(apiKey);
    if (!ai) return null;

    // Helper to find first available temp
    const getTemp = (p: WeatherDataPoint) => {
        return p.temperature_2m_best_match || 
               p.temperature_2m_metno_nordic || 
               p.temperature_2m_smhi_seamless || 
               p.temperature_2m_ecmwf_ifs04 || 
               0;
    };

    // Summarize next 12 hours for the prompt
    const next12Hours = forecast.slice(0, 12).map(p => ({
        t: p.time,
        temp: getTemp(p),
        rain: p.precip,
        wind: p.windSpeed,
        gusts: p.windGusts
    }));

    const currentTemp = getTemp(currentWeather);

    const prompt = `
        Current weather: Temp ${currentTemp}, Wind ${currentWeather.windSpeed}m/s, Rain ${currentWeather.precip}mm.
        Next 12 hours summary: ${JSON.stringify(next12Hours)}.
        Language: ${getLanguageName(lang)}.
        
        Provide:
        1. Clothing advice (specific layers).
        2. Sailing score/advice.
        3. Gardening score/advice.
        4. A short scientific summary of the weather system.
    `;

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
            config: {
                responseMimeType: 'application/json',
                responseSchema: {
                    type: Type.OBJECT,
                    properties: {
                        clothing: { type: Type.STRING },
                        activities: {
                            type: Type.OBJECT,
                            properties: {
                                sailing: { type: Type.STRING },
                                gardening: { type: Type.STRING }
                            }
                        },
                        summary: { type: Type.STRING }
                    }
                }
            }
        });

        if (response.text) {
            return JSON.parse(response.text) as GeminiInsight;
        }
        return null;
    } catch (e) {
        console.error("Gemini analysis failed", e);
        return null;
    }
};
