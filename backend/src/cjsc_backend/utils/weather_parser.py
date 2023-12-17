#!/usr/bin/env python3
import requests
import json

from cjsc_backend.http.schemas.weather import \
    WeatherInfoSchema


def get_weather() -> WeatherInfoSchema:
    weather_data_raw = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "appid": "e1221a90440361935a648cd882556330",
            "lat": "62.541028",
            "lon": "113.978701",
            "units": "metric",
        }
    ).content

    weather_data = json.loads(weather_data_raw)

    return WeatherInfoSchema(
        main=weather_data["weather"][0]["main"],
        description=weather_data["weather"][0]["description"],
        temp=weather_data["main"]["temp"],
        feels_like=weather_data["main"]["feels_like"],
        temp_min=weather_data["main"]["temp_min"],
        temp_max=weather_data["main"]["temp_max"],
        pressure=weather_data["main"]["pressure"],
        humidity=weather_data["main"]["humidity"],
        visibility=weather_data["visibility"],
        wind_speed=weather_data["wind"]["speed"],
    )


def create_weather_message() -> str:
    weather = get_weather()
    msg_text = "☁️ Weather for today in Mirny\n\n"
    msg_text += f"Weather: {weather.main}\n"
    msg_text += f"Detailed: {weather.description}\n"
    msg_text += f"Temperature: {weather.temp}C \
(max: {weather.temp_max}C, min: {weather.temp_min}C)\n"
    msg_text += f"Pressure: {weather.pressure} mmHg\n"
    msg_text += f"Humidity: {weather.humidity}%\n"
    msg_text += f"Visibility: {weather.visibility} meters\n"
    msg_text += f"Wind speed: {weather.wind_speed}\n"

    return msg_text
