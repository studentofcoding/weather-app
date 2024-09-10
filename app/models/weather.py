from pydantic import BaseModel, Field

class WeatherResponse(BaseModel):
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    description: str = Field(..., description="Weather description")

    class Config:
        schema_extra = {
            "example": {
                "city": "London",
                "temperature": 25.5,
                "humidity": 60.0,
                "wind_speed": 5.2,
                "description": "Partly cloudy"
            }
        }