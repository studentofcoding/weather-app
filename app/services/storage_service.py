import json
import os
from datetime import datetime, timedelta
from typing import Optional
from app.models.weather import WeatherResponse
import logging
logger = logging.getLogger(__name__)

STORAGE_DIR = "weather_data"

# Ensure the STORAGE_DIR exists
os.makedirs(STORAGE_DIR, exist_ok=True)

async def store_weather_data(coord: str, data: WeatherResponse):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    filename = f"{coord}@{timestamp}.json"
    filepath = os.path.join(STORAGE_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(data.dict(), f)

async def get_cached_weather_data(coord: str) -> Optional[WeatherResponse]:
    try:
        files = os.listdir(STORAGE_DIR)
    except FileNotFoundError:
        return None

    now = datetime.utcnow()
    
    for file in reversed(files):
        if file.startswith(f"{coord}@"):
            filepath = os.path.join(STORAGE_DIR, file)
            try:
                # Extract timestamp from filename
                timestamp_str = file.split("@")[1].split(".")[0]
                file_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
                
                if now - file_time <= timedelta(minutes=5):
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    return WeatherResponse(**data)
                else:
                    # Remove expired cache file
                    os.remove(filepath)
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing timestamp from filename {file}: {str(e)}")
                continue
    
    return None