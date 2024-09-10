from fastapi import FastAPI, HTTPException, Query
from app.services.weather_service import get_weather_data
from app.services.geocoding_service import get_coordinates
from app.services.storage_service import store_weather_data, get_cached_weather_data
from app.services.database_service import log_weather_event
from app.models.weather import WeatherResponse
import asyncio
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

app = FastAPI()

def validate_weather_data(weather_data: Dict[str, Any]) -> None:
    """Validate weather data and raise an exception if any value is None."""
    for key, value in weather_data.items():
        if value is None:
            raise ValueError(f"Invalid weather data: {key} is None")
        if not isinstance(value, (str, int, float)):
            raise ValueError(f"Invalid type for {key}: expected str, int, or float, got {type(value)}")

@app.get("/weather", response_model=WeatherResponse)
async def get_weather(city: str = Query(..., min_length=1)):
    logger.info(f"Received weather request for city: {city}")
    try:
        # Get coordinates for the city
        logger.info(f"Fetching coordinates for city: {city}")
        coordinates = await get_coordinates(city)
        if not coordinates:
            logger.warning(f"City not found: {city}")
            raise HTTPException(status_code=404, detail=f"City not found: {city}")
        
        lat, lon = coordinates
        logger.info(f"Coordinates for {city}: lat={lat}, lon={lon}")

        # Check cache first
        logger.info(f"Checking cache for coordinates: lat={lat}, lon={lon}")
        cached_data = await get_cached_weather_data(f"{lat}_{lon}")
        if cached_data:
            logger.info(f"Cache hit for coordinates: lat={lat}, lon={lon}")
            logger.debug(f"Cached weather data: {cached_data}")
            return cached_data

        # Fetch new data if not in cache
        logger.info(f"Cache miss. Fetching new weather data for coordinates: lat={lat}, lon={lon}")
        try:
            weather_data = await get_weather_data(lat, lon)
        except ValueError as ve:
            logger.error(f"Error fetching weather data: {ve}")
            raise HTTPException(status_code=500, detail=str(ve))

        logger.debug(f"Received weather data: {weather_data}")

        # Store data and log event concurrently
        logger.info(f"Storing weather data and logging event for city: {city}")
        await asyncio.gather(
            store_weather_data(f"{lat}_{lon}", weather_data),
            log_weather_event(city, weather_data)
        )

        logger.info(f"Successfully retrieved and processed weather data for city: {city}")
        return weather_data
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=500, detail=str(ve))
    except HTTPException as http_exc:
        logger.error(f"HTTP exception occurred: {str(http_exc)}")
        raise http_exc
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")