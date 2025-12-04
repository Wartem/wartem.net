
import { WeatherModel } from './types';

export const SHARED_CONFIG = {
  "language": "sv",
  "locations": [
    { "id": "loc_home", "name": "Malmö", "lat": 55.60498, "lng": 13.00382, "country": "Sverige" },
    { "id": "loc_sthlm", "name": "Stockholm", "lat": 59.3293, "lng": 18.0686, "country": "Sverige" },
    { "id": "loc_gbg", "name": "Göteborg", "lat": 57.7089, "lng": 11.9746, "country": "Sverige" }
  ],
  "activeLocationId": "loc_home",
  "activeModels": [
    WeatherModel.SMHI,
    WeatherModel.YR,
    WeatherModel.DMI,
    WeatherModel.ECMWF
  ]
} as const;
