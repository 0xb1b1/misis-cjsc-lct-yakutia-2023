#!/usr/bin/env python3
import requests
from urllib import parse as urlparse
from loguru import logger
from datetime import datetime, UTC

from cjsc_vk_bot import config

from cjsc_vk_bot.http.schemas.weather import \
    WeatherInfoSchema

from cjsc_vk_bot.http.schemas.message import \
    MessagePlatform, MessageRequestType, \
    MessageSchema


def get_weather_message(msg: MessageSchema) -> MessageSchema:
    logger.debug("Quering Backend for Weather Message")

    response_raw = requests.post(
        urlparse.urljoin(
            config.BACKEND_URL,
            "/weather/get_weather_message",
        ),
        data=msg,
    )
    logger.debug(
        f"Received a JSON response: {response_raw.content}"
    )

    if response_raw.status_code != 200:
        logger.warning(
            f"Weather message request to Backend status code != 200: \
{response_raw.status_code}"
        )

        return msg

    try:
        response = MessageSchema.model_validate_json(response_raw.content)
    except Exception as exc:
        logger.error(
            f"An error occured while parsing Backend Response: \
({response_raw.status_code=}, {response_raw.content}), {exc}"
        )
        return msg

    logger.debug(
        f"Parsed a response from Backend Weather Data: {response}"
    )

    return response
