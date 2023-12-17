#!/usr/bin/env python3
import requests
from urllib import parse as urlparse
from loguru import logger
import json

from cjsc_vk_bot import config

from cjsc_vk_bot.http.schemas.message import \
    MessageSchema  # , MessagePlatform

from cjsc_vk_bot.http.schemas.user import \
    UserPreferencesSchema, \
    UserLanguagePreference


def get_user_prefs(user_id: str) -> UserPreferencesSchema:
    response_raw = requests.get(
        urlparse.urljoin(
            config.BACKEND_URL,
            "/users/get_preferences"
        ),
        params={
            "platform": "vk",
            "user_id": user_id,
        },
    )

    if response_raw.status_code != 200:
        logger.critical(
            f"Backend answered with non-200 code for Get User Preferences \
({user_id=})",
        )
        raise ValueError("User preferences not retrieved")  # Return default value?  # noqa: E501

    try:
        prefs = UserPreferencesSchema.model_validate_json(response_raw.content)
    except Exception as exc:
        logger.error(
            f"An error occured while parsing Backend Response: \
({response_raw.status_code=}, {response_raw.content}), {exc}"
        )
        raise ValueError("User preferences failed to parse")

    return prefs


def translate_message(msg: MessageSchema, prefs: UserPreferencesSchema):
    if prefs.language == UserLanguagePreference.RU:
        logger.debug(
            f"User's preferred language is RU; not translating \
({prefs=})"
        )
        return msg

    msg_json: str = json.dumps(
        msg.model_dump(),
        indent=4,
        default=str,
        ensure_ascii=True,
    )
    logger.debug(f"Quering Backend for translated message: {msg_json}")

    response_raw = requests.post(
        urlparse.urljoin(
            config.BACKEND_URL,
            "/utils/message/translate",
        ),
        data=msg_json,
    )
    logger.debug(
        f"Received a JSON response: {response_raw.content}"
    )

    if response_raw.status_code != 200:
        logger.warning(
            f"Translate request to Backend status code != 200: \
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
        f"Parsed a response from Backend Translate: {response}"
    )

    return response


def query_ml(
    msg: MessageSchema,
    prefs: UserPreferencesSchema
) -> MessageSchema:
    """Queries the service with ML model.

    Args:
        msg (MessageSchema): Schema with None in response_text.

    Returns:
        MessageSchema: Schema with None in request_text.
    """
    se_link = "https://ya.ru/search/?text=" + urlparse.quote(msg.request_text)

    msg_json: str = json.dumps(
        msg.model_dump(),
        indent=4,
        default=str,
        ensure_ascii=True,
    )
    logger.debug(
        f"Querying ML Model for response: {msg_json}"  # noqa: E501
    )

    response_raw = requests.post(
        urlparse.urljoin(config.ML_URL, "/msg/answer"),
        data=msg_json,
    )
    logger.debug(
        f"Received a JSON response: {response_raw.content}"
    )

    try:
        response = MessageSchema.model_validate_json(response_raw.content)
    except Exception as exc:
        logger.error(
            f"An error occured while parsing ML Response: \
({response_raw.status_code=}, {response_raw.content}), {exc}"
        )
        return MessageSchema(
            platform=msg.platform,
            user_id=msg.user_id,
            timestamp=msg.timestamp,
            request_text=None,
            response_text="Кажется что-то сломалось.\n\
Но мы уже знаем и стараемся починить — напишите нам позже",
            request_type=None,
        )

    logger.debug(
        f"Parsed a response from from ML Model: {response}"
    )

    response = translate_message(response, prefs)

    # Add link to the search engine
    response.response_text = response.response_text \
        + f"\n\nНе нашли то, что искали? \
Попробуйте поиск: {se_link}"

    return response
