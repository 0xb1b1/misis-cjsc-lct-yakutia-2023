#!/usr/bin/env python3
from pydantic import BaseModel


class WeatherInfoSchema(BaseModel):
    main: str
    description: str
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    visibility: int
    wind_speed: float
