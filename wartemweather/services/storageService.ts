
import { AppConfig, WeatherCache, WeatherModel, Location } from '../types';
import { DEFAULT_CONFIG } from '../constants';
import { SHARED_CONFIG } from '../config';

const CONFIG_KEY = 'wartem_weather_config_v1';
const CACHE_KEY_PREFIX = 'wartem_cache_';

export const saveConfig = (config: AppConfig): void => {
  try {
    localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
  } catch (e) {
    console.error("Failed to save config", e);
  }
};

export const loadConfig = (): AppConfig => {
  try {
    // 1. Try to get user overrides from localStorage
    const stored = localStorage.getItem(CONFIG_KEY);
    
    // 2. Prepare the Base Config (Source of Truth is config.ts)
    const baseConfig: AppConfig = {
        language: (SHARED_CONFIG.language as any) || DEFAULT_CONFIG.language,
        locations: (SHARED_CONFIG.locations as unknown as Location[]) || DEFAULT_CONFIG.locations,
        activeLocationId: SHARED_CONFIG.activeLocationId || DEFAULT_CONFIG.activeLocationId,
        activeModels: (SHARED_CONFIG.activeModels as unknown as WeatherModel[]) || DEFAULT_CONFIG.activeModels
    };

    if (!stored) return baseConfig;

    // 3. If localStorage exists, we merge it, BUT we prioritize config.ts for Locations
    // This allows you to update locations in the file and have them propagate to devices
    const localConfig = JSON.parse(stored);

    // If the shared file has DIFFERENT locations than what is saved in local storage,
    // we assume the user updated the file and wants to see those changes.
    const fileLocs = SHARED_CONFIG.locations as unknown as Location[];
    
    // Simple check: different length or different first ID
    if (fileLocs.length !== localConfig.locations?.length || 
        fileLocs[0]?.id !== localConfig.locations?.[0]?.id) {
        console.log("Shared config locations updated, resetting local location cache.");
        localConfig.locations = fileLocs;
    }

    return { ...baseConfig, ...localConfig };
  } catch (e) {
    console.error("Failed to load config, using default", e);
    return DEFAULT_CONFIG;
  }
};

export const saveCache = (locationId: string, data: WeatherCache): void => {
  try {
    localStorage.setItem(`${CACHE_KEY_PREFIX}${locationId}`, JSON.stringify(data));
  } catch (e) {
    // If quota exceeded, clear old caches
    try {
        console.warn("Quota exceeded, pruning old cache...");
        localStorage.clear();
        localStorage.setItem(`${CACHE_KEY_PREFIX}${locationId}`, JSON.stringify(data));
    } catch (inner) {
        console.error("Cache write failed completely", inner);
    }
  }
};

export const loadCache = (locationId: string): WeatherCache | null => {
  try {
    const stored = localStorage.getItem(`${CACHE_KEY_PREFIX}${locationId}`);
    return stored ? JSON.parse(stored) : null;
  } catch (e) {
    return null;
  }
};
