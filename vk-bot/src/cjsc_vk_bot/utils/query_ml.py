#!/usr/bin/env python3
import requests
from urllib import parse as urlparse
from loguru import logger
import json

from cjsc_vk_bot import config

from cjsc_vk_bot.http.schemas.message import \
    MessageSchema  # , MessagePlatform


def query_ml(msg: MessageSchema) -> MessageSchema:
    """Queries the service with ML model.

    Args:
        msg (MessageSchema): Schema with None in response_text.

    Returns:
        MessageSchema: Schema with None in request_text.
    """
    se_link = "https://ya.ru/search/?text=" + urlparse.quote(msg.request_text)  # TODO: use the seatch link

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

    # Add link to the search engine
    response.response_text = response.response_text + f"\n\nНе нашли то, что искали? \
Попробуйте поиск: {se_link}"

    return response
