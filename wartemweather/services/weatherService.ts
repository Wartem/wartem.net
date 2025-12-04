
import { Location, WeatherModel, WeatherCache, WeatherDataPoint, DailyData } from '../types';
import { saveCache, loadCache } from './storageService';

const FORECAST_URL = 'https://api.open-meteo.com/v1/forecast';
const MARINE_URL = 'https://marine-api.open-meteo.com/v1/marine';
const AIR_QUALITY_URL = 'https://air-quality-api.open-meteo.com/v1/air-quality';
const ARCHIVE_URL = 'https://archive-api.open-meteo.com/v1/archive';
const GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search';

interface FetchOptions {
  location: Location;
  models: WeatherModel[];
  forceRefresh?: boolean;
  signal?: AbortSignal;
}

// Helper: Fetch with timeout and AbortSignal support
const fetchWithTimeout = async (url: string, timeout = 25000, parentSignal?: AbortSignal) => {
    if (parentSignal?.aborted) {
        throw new DOMException('Aborted by user', 'AbortError');
    }

    const controller = new AbortController();
    
    // Wire up parent signal
    const onAbort = () => controller.abort();
    if (parentSignal) {
        parentSignal.addEventListener('abort', onAbort);
    }

    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
        }
        return response;
    } catch (error: any) {
        // Enhance error message if it's a timeout
        if (error.name === 'AbortError' && !parentSignal?.aborted) {
             throw new Error(`Request timed out after ${timeout}ms`);
        }
        throw error;
    } finally {
        clearTimeout(timeoutId);
        if (parentSignal) {
            parentSignal.removeEventListener('abort', onAbort);
        }
    }
};

const getHistoricalDateRange = () => {
  const now = new Date();
  const start = new Date(now);
  start.setFullYear(start.getFullYear() - 1);
  start.setDate(start.getDate() - 1); 
  const end = new Date(now);
  end.setFullYear(end.getFullYear() - 1);
  end.setDate(end.getDate() + 3); 

  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  };
};

export const searchLocations = async (query: string): Promise<Location[]> => {
  if (!query || query.length < 2) return [];
  try {
    const url = `${GEOCODING_URL}?name=${encodeURIComponent(query)}&count=5&language=sv&format=json`;
    const res = await fetchWithTimeout(url);
    const data = await res.json();
    if (!data.results) return [];
    
    return data.results.map((item: any) => ({
      id: `loc_${item.id}`,
      name: item.name,
      lat: item.latitude,
      lng: item.longitude,
      country: item.country,
      admin1: item.admin1
    }));
  } catch (e) {
    console.error("Geocoding failed", e);
    return [];
  }
};

export const getWeatherData = async ({ location, models, forceRefresh = false, signal }: FetchOptions): Promise<WeatherCache> => {
  if (!location || !location.id || !location.lat || !location.lng) throw new Error("Invalid location data");
  
  const cached = loadCache(location.id);
  const now = Date.now();
  const CACHE_DURATION = 1000 * 60 * 10; // 10 minutes

  if (!forceRefresh && cached && (now - cached.timestamp < CACHE_DURATION)) {
    console.log(`Using cached data for ${location.name} (Age: ${((now - cached.timestamp)/1000).toFixed(0)}s)`);
    return cached;
  }

  console.log(`Fetching new data for ${location.name}...`);

  const latLng = `latitude=${location.lat}&longitude=${location.lng}`;
  const timeParams = `timezone=auto&past_days=1&forecast_days=4`;

  // --- 1. SETUP URLS ---
  
  // A. Main Weather URL (Hourly + Models)
  const uniqueModels = new Set(models || [WeatherModel.SMHI]);
  uniqueModels.add(WeatherModel.ECMWF); // Force ECMWF for scientific data
  const modelStr = Array.from(uniqueModels).join(',');

  const hourlyParams = [
    'temperature_2m', 'precipitation', 'pressure_msl', 'wind_speed_10m', 'wind_gusts_10m', 'wind_direction_10m',
    'relative_humidity_2m', 'cloud_cover_low', 'cloud_cover_mid', 'cloud_cover_high', 
    'weather_code',
    // Scientific Params (will use ECMWF automagically or best_match if available)
    'uv_index', 'soil_temperature_0cm', 'soil_temperature_18cm', 'soil_moisture_0_to_1cm', 'cape', 'visibility'
  ].join(',');

  const weatherUrl = `${FORECAST_URL}?${latLng}&${timeParams}&hourly=${hourlyParams}&models=${modelStr}&wind_speed_unit=ms`;

  // B. Astro URL (Daily - NO Models)
  const dailyParams = 'sunrise,sunset,daylight_duration,moon_phase';
  const astroUrl = `${FORECAST_URL}?${latLng}&${timeParams}&daily=${dailyParams}`;

  // C. Aux URLs
  const marineUrl = `${MARINE_URL}?${latLng}&${timeParams}&hourly=wave_height,wave_direction`;
  const aqiUrl = `${AIR_QUALITY_URL}?${latLng}&${timeParams}&hourly=european_aqi,pm2_5,birch_pollen,grass_pollen,mugwort_pollen`;
  
  const { start, end } = getHistoricalDateRange();
  const histUrl = `${ARCHIVE_URL}?${latLng}&start_date=${start}&end_date=${end}&hourly=temperature_2m,wind_speed_10m,precipitation&timezone=auto&wind_speed_unit=ms`;

  // --- 2. EXECUTE FETCHES ---
  
  let mainJson: any = null;
  let astroJson: any = null;
  let marineJson: any = null;
  let aqiJson: any = null;
  let historicalData: WeatherDataPoint[] = [];

  try {
      // Run critical fetches
      const results = await Promise.allSettled([
          fetchWithTimeout(weatherUrl, 25000, signal),
          fetchWithTimeout(astroUrl, 15000, signal),
          fetchWithTimeout(marineUrl, 15000, signal),
          fetchWithTimeout(aqiUrl, 15000, signal),
          fetchWithTimeout(histUrl, 20000, signal)
      ]);

      // Process Main Weather (CRITICAL)
      // Unwrap logic: If critical request fails, check if it was aborted
      if (results[0].status === 'fulfilled') {
          mainJson = await results[0].value.json();
      } else {
          const reason = results[0].reason;
          if (reason.name === 'AbortError') {
              throw reason; // Re-throw AbortError directly
          }
          throw new Error(`Weather Fetch Failed: ${reason.message || reason}`);
      }

      // Process Astro
      if (results[1].status === 'fulfilled') astroJson = await results[1].value.json();
      
      // Process Marine
      if (results[2].status === 'fulfilled') marineJson = await results[2].value.json();
      
      // Process AQI
      if (results[3].status === 'fulfilled') aqiJson = await results[3].value.json();

      // Process Historical
      if (results[4].status === 'fulfilled') {
          const json = await results[4].value.json();
          historicalData = mapHistoricalData(json);
      }

  } catch (e: any) {
      if (e.name === 'AbortError') throw e; // Pass AbortError up to UI to be ignored
      console.error("Fetch Logic Error:", e);
      throw e;
  }

  // --- 3. MAPPING ---
  let processedData: WeatherDataPoint[] = [];
  try {
      processedData = mapMergedData(mainJson, marineJson, aqiJson, Array.from(uniqueModels));
  } catch (e) {
      console.error("Mapping failed", e);
      // Don't crash entire app on mapping error, but maybe return empty or cached
      throw new Error("Failed to process weather data");
  }

  // Daily Data Extraction
  let dailyData: DailyData | null = null;
  if (astroJson?.daily) {
      const d = astroJson.daily;
      if (d.time && d.sunrise && d.sunset) {
          dailyData = {
              time: d.time,
              sunrise: d.sunrise,
              sunset: d.sunset,
              moonPhase: d.moon_phase,
              daylightDuration: d.daylight_duration
          };
      }
  }

  const newCache: WeatherCache = {
      timestamp: now,
      elevation: mainJson?.elevation || 0,
      data: processedData,
      daily: dailyData,
      historical: historicalData
  };

  saveCache(location.id, newCache);
  return newCache;
};

// --- Mappers ---

const mapMergedData = (forecast: any, marine: any, aqi: any, models: WeatherModel[]): WeatherDataPoint[] => {
    if (!forecast || !forecast.hourly || !Array.isArray(forecast.hourly.time)) return [];
    
    const count = forecast.hourly.time.length;
    const result: WeatherDataPoint[] = [];
    const primaryModel = models[0]; 

    for (let i = 0; i < count; i++) {
        const time = forecast.hourly.time[i];
        if (!time) continue;

        const point: WeatherDataPoint = { time };

        const getVal = (prefix: string, model: string) => {
            const key = `${prefix}_${model}`;
            const val = forecast.hourly[key]?.[i];
            if (val !== undefined && val !== null) return val;
            if (model === 'best_match') return forecast.hourly[prefix]?.[i];
            return undefined;
        };

        // 1. Comparison Data
        models.forEach(model => {
            const temp = getVal('temperature_2m', model);
            if (temp !== undefined) point[`temperature_2m_${model}`] = temp;

            const wind = getVal('wind_speed_10m', model);
            if (wind !== undefined) point[`wind_speed_10m_${model}`] = wind;

            const precip = getVal('precipitation', model);
            if (precip !== undefined) point[`precipitation_${model}`] = precip;
        });

        // 2. Primary Metrics
        const getPrimary = (key: string) => {
            return getVal(key, primaryModel) ?? getVal(key, 'best_match') ?? forecast.hourly[key]?.[i] ?? 0;
        };

        point.precip = Number(getPrimary('precipitation'));
        point.pressure = Number(getVal('pressure_msl', primaryModel) ?? forecast.hourly.pressure_msl?.[i] ?? 1013);
        point.windSpeed = Number(getPrimary('wind_speed_10m'));
        point.windGusts = Number(getVal('wind_gusts_10m', primaryModel) ?? forecast.hourly.wind_gusts_10m?.[i] ?? 0);
        point.windDirection = Number(getVal('wind_direction_10m', primaryModel) ?? forecast.hourly.wind_direction_10m?.[i] ?? 0);
        point.humidity = Number(getVal('relative_humidity_2m', primaryModel) ?? forecast.hourly.relative_humidity_2m?.[i] ?? 0);
        
        point.cloudLow = Number(getVal('cloud_cover_low', primaryModel) ?? forecast.hourly.cloud_cover_low?.[i] ?? 0);
        point.cloudMid = Number(getVal('cloud_cover_mid', primaryModel) ?? forecast.hourly.cloud_cover_mid?.[i] ?? 0);
        point.cloudHigh = Number(getVal('cloud_cover_high', primaryModel) ?? forecast.hourly.cloud_cover_high?.[i] ?? 0);
        point.weatherCode = getVal('weather_code', primaryModel) ?? forecast.hourly.weather_code?.[i] ?? 0;

        // 3. Scientific (Fallback to ECMWF)
        const getSci = (key: string) => {
             return getVal(key, primaryModel) ?? getVal(key, WeatherModel.ECMWF) ?? forecast.hourly[key]?.[i];
        };

        point.uvIndex = Number(getSci('uv_index') ?? 0);
        point.cape = Number(getSci('cape') ?? 0);
        point.visibility = Number(getSci('visibility') ?? 0);
        point.soilTemp0cm = getSci('soil_temperature_0cm');
        point.soilTemp18cm = getSci('soil_temperature_18cm');
        point.soilMoisture = getSci('soil_moisture_0_to_1cm');
        
        // Mock Kp
        const hour = new Date(time).getHours();
        point.kp = Math.max(0, 2 + Math.sin(hour / 4) + (Math.random() * 2));

        // 4. Marine
        if (marine?.hourly?.time) {
            const mIdx = marine.hourly.time.indexOf(time);
            if (mIdx !== -1) {
                point.waveHeight = marine.hourly.wave_height?.[mIdx];
                point.waveDirection = marine.hourly.wave_direction?.[mIdx];
            }
        }

        // 5. AQI
        if (aqi?.hourly?.time) {
            const aIdx = aqi.hourly.time.indexOf(time);
            if (aIdx !== -1) {
                point.aqi = aqi.hourly.european_aqi?.[aIdx];
                point.pm25 = aqi.hourly.pm2_5?.[aIdx];
                point.pollenBirch = aqi.hourly.birch_pollen?.[aIdx];
                point.pollenGrass = aqi.hourly.grass_pollen?.[aIdx];
                point.pollenMugwort = aqi.hourly.mugwort_pollen?.[aIdx];
            }
        }

        result.push(point);
    }
    return result;
};

const mapHistoricalData = (json: any): WeatherDataPoint[] => {
    if (!json || !json.hourly || !Array.isArray(json.hourly.time)) return [];
    return json.hourly.time.map((time: string, i: number) => ({
        time,
        temp_historical: json.hourly.temperature_2m?.[i],
        wind_historical: json.hourly.wind_speed_10m?.[i],
        precip_historical: json.hourly.precipitation?.[i]
    }));
};
