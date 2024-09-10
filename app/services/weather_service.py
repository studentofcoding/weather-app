import aiohttp
from app.models.weather import WeatherResponse
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger(__name__)

async def get_weather_data(lat: float, lon: float) -> WeatherResponse:
    API_KEY = os.getenv("WEATHER_API_KEY")
    if not API_KEY:
        logger.error("OpenWeatherMap API key is missing")
        raise ValueError("OpenWeatherMap API key is not configured")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    async with aiohttp.ClientSession() as session:
        logger.info(f"get weather request to {url}")
        async with session.get(url) as response:
            if response.status == 401:
                logger.error("Failed to authenticate with OpenWeatherMap API. Check your API key.")
                raise ValueError("Invalid API key for OpenWeatherMap")
            elif response.status != 200:
                logger.error(f"Failed to fetch weather data: HTTP {response.status}")
                raise ValueError(f"Failed to fetch weather data: HTTP {response.status}")

            data = await response.json()
            logger.debug(f"Raw weather data: {data}")

            try:
                weather_data = WeatherResponse(
                    city=data['name'],
                    temperature=data['main']['temp'],
                    humidity=data['main']['humidity'],
                    wind_speed=data['wind']['speed'],
                    description=data['weather'][0]['description']
                )
                logger.info(f"Processed weather data: {weather_data}")
                return weather_data
            except KeyError as e:
                logger.error(f"Missing key in weather data: {e}")
                raise ValueError(f"Incomplete weather data: missing {e}")
            except Exception as e:
                logger.error(f"Error processing weather data: {e}")
                raise ValueError(f"Error processing weather data: {e}")