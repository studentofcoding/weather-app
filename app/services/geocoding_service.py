import aiohttp
import logging
from typing import Optional, Tuple
import os

logger = logging.getLogger(__name__)

async def get_coordinates(city: str) -> Optional[Tuple[float, float]]:
    API_KEY = os.getenv("WEATHER_API_KEY")
    if not API_KEY:
        logger.error("OpenWeatherMap API key is missing")
        raise ValueError("OpenWeatherMap API key is not configured")

    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        logger.info(f"Geocoding result for {city}: lat={lat}, lon={lon}")
                        return lat, lon
                    else:
                        logger.warning(f"Geocoding failed for {city}: No location found")
                        return None
                else:
                    logger.error(f"Geocoding failed for {city}: HTTP status {response.status}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Geocoding error for {city}: {str(e)}")
            return None