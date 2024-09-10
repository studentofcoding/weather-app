import json
import os
from datetime import datetime
from app.models.weather import WeatherResponse

DB_FILE = "weather_events.json"

async def log_weather_event(city: str, data: WeatherResponse):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    event = {
        "city": city,
        "timestamp": timestamp,
        "storage_path": f"weather_data/{city}@{timestamp}.json"
    }
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            events = json.load(f)
    else:
        events = []
    
    events.append(event)
    
    with open(DB_FILE, "w") as f:
        json.dump(events, f)