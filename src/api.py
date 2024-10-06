import requests
from typing import Dict, Any
import logging
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_rainfall_data(self, date: str = None) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/rainfall"
        params = {"date": date} if date else {}

        try:
            logger.debug(f"Sending request to {endpoint} with params {params}")
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Full API response: {json.dumps(data, indent=2)}")
            return data
        except requests.RequestException as e:
            logger.error(f"Error fetching rainfall data: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def parse_rainfall_data(self, data: Dict[str, Any]) -> Dict[str, float]:
        logger.debug(f"Parsing rainfall data: {json.dumps(data, indent=2)}")
        rainfall_data = {}
        if data and 'data' in data:
            stations = {station['id']: station for station in data['data'].get('stations', [])}
            readings = data['data'].get('readings', [])
            logger.debug(f"Number of stations: {len(stations)}")
            logger.debug(f"Number of readings: {len(readings)}")
            
            latest_reading = readings[-1] if readings else None
            if latest_reading:
                for station_data in latest_reading.get('data', []):
                    station_id = station_data.get('stationId')
                    value = station_data.get('value')
                    station_info = stations.get(station_id, {})
                    lat = station_info.get('location', {}).get('latitude')
                    lon = station_info.get('location', {}).get('longitude')
                    
                    if station_id and value is not None and lat and lon:
                        rainfall_data[station_id] = {
                            'value': value,
                            'lat': lat,
                            'lon': lon,
                            'name': station_info.get('name', '')
                        }
                    else:
                        logger.warning(f"Incomplete data for station {station_id}")
            else:
                logger.warning("No readings found in the data")
        else:
            logger.error("Invalid data structure received from API")
        
        logger.debug(f"Parsed rainfall data: {json.dumps(rainfall_data, indent=2)}")
        return rainfall_data