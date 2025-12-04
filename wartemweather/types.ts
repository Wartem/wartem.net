
export enum WeatherModel {
  SMHI = 'best_match',
  YR = 'metno_nordic',
  DMI = 'dmi_seamless',
  ECMWF = 'ecmwf_ifs04',
  ICON = 'icon_seamless',
  GFS = 'gfs_seamless',
}

export enum Language {
  SV = 'sv',
  EN = 'en',
  DE = 'de',
  FR = 'fr',
  ES = 'es'
}

export interface Location {
  id: string;
  name: string;
  lat: number;
  lng: number;
  country?: string;
  admin1?: string;
}

export interface AppConfig {
  language: Language;
  locations: Location[];
  activeLocationId: string;
  activeModels: WeatherModel[];
  geminiApiKey?: string; // New field for browser-stored key
  lastUpdated?: number;
}

export interface DailyData {
    time: string[];
    sunrise: string[];
    sunset: string[];
    moonPhase?: number[]; // 0.0 to 1.0
    daylightDuration?: number[]; // seconds
}

export interface WeatherDataPoint {
  time: string; // ISO String
  
  // Base
  temp?: number;
  windSpeed?: number;
  windGusts?: number;
  windDirection?: number;
  precip?: number;
  humidity?: number;
  pressure?: number;
  cloudLow?: number;
  cloudMid?: number;
  cloudHigh?: number;
  weatherCode?: number;
  thunderRisk?: number;
  kp?: number;

  // Scientific / Advanced
  cape?: number; // Convective Available Potential Energy (J/kg)
  visibility?: number; // meters

  // Historical Comparisons
  temp_historical?: number;
  wind_historical?: number;
  precip_historical?: number;

  // Dynamic Model Keys (e.g. temperature_2m_best_match)
  [key: string]: number | string | undefined;

  // New Features
  uvIndex?: number;
  
  // Marine
  waveHeight?: number;
  waveDirection?: number;
  
  // Nature / Bio
  aqi?: number; // European AQI
  pm25?: number;
  pollenBirch?: number;
  pollenGrass?: number;
  pollenMugwort?: number;
  
  // Gardening
  soilTemp0cm?: number;
  soilTemp18cm?: number;
  soilMoisture?: number;
}

export interface WeatherCache {
  timestamp: number;
  elevation: number;
  data: WeatherDataPoint[];
  daily: DailyData | null;
  historical?: WeatherDataPoint[]; // For the "Time Machine"
}

export interface GeminiInsight {
  clothing: string;
  activities: {
    sailing: string;
    gardening: string;
  };
  summary: string;
}
