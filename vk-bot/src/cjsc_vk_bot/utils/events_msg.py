#!/usr/bin/env python3
import requests
from urllib import parse as urlparse
from loguru import logger
from datetime import datetime, UTC

from cjsc_vk_bot import config

from cjsc_vk_bot.http.schemas.event import \
    CityEvent, CityEvents

from cjsc_backend.http.schemas.message import \
    MessagePlatform, MessageRequestType, \
    MessageSchema


def get_events() -> CityEvents:
    logger.info("Getting City Events from Backend")
    r = requests.get(
        urlparse.urljoin(
            config.BACKEND_URL,
            "/events/get_events",
        )
    )

    if r.status_code != 200:
        logger.critical(
            f"Failed to fetch news from backend \
({r.status_code=}, {r.content=}), returning empty list"
        )
        return CityEvents(
            events=[],
        )

    try:
        events = CityEvents.model_validate_json(r.content)
    except Exception as exc:
        logger.critical(
            f"Something went wrong while parsing City Events \
({exc})"
        )
        return CityEvents(
            events=[],
        )

    logger.debug(
        f"Got City Events from Backend: {events}"
    )

    return events


def create_events_message() -> MessageSchema:
    events = get_events().events
    if len(events) == 0:
        return MessageSchema(
            platform=MessagePlatform.VK,
            user_id="nullstring",
            timestamp=datetime.now(UTC),
            request_text=None,
            response_text="К сожалению, новости не найдены. \
Пожалуйста, попробуйте позже!",
        )
    msg_text = "События на сегодня\n\n"

    for event in events:
        msg_text += f"{event.title}\n\n{event.description}\
\n\n{event.link}\n---\n\n"

    return MessageSchema(
        platform=MessagePlatform.VK,
        user_id="nullstring",
        timestamp=datetime.now(UTC),
        request_text=None,
        response_text=msg_text,
    )
