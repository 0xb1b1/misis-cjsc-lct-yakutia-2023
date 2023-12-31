#!/usr/bin/env python3
import sys
from loguru import logger
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
from pydantic import ValidationError

from cjsc_vk_bot import config
from cjsc_vk_bot.models.vk_message import vk_message_from_event
from cjsc_vk_bot.utils.query_ml import query_ml, \
    get_user_prefs
from cjsc_vk_bot.http.schemas.message import \
    MessageSchema, MessagePlatform, MessageRequestType

from cjsc_vk_bot.utils.events_msg import \
    create_events_message

from cjsc_vk_bot.utils.weather_msg import \
    get_weather_message

vk_session = vk_api.VkApi(token=config.VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 223871238)


def send_message(id: int, message_text: str):
    vk_session.method(
        "messages.send",
        {
            "user_id": id,
            "message": message_text,
            "random_id": 0
        }
    )


def run():
    # Set up Loguru
    logger.remove()
    logger.add(sys.stderr, level=config.LOGGING_LEVEL)
    logger.critical(f"Logging level set to {config.LOGGING_LEVEL}.")

    # Listen for VK events
    for event in longpoll.listen():
        message = vk_message_from_event(event)
        if event.type == VkBotEventType.MESSAGE_NEW:
            logger.info(
                f"Message from {message.from_user.id}: {message.text}",
            )
            user_prefs = get_user_prefs(str(message.from_user.id))
            try:
                msg = MessageSchema(
                    platform=MessagePlatform.VK,
                    user_id=str(message.from_user.id),
                    timestamp=message.timestamp,
                    request_text=message.text,
                    response_text=None,
                    request_type=None,
                )
            except ValidationError:
                logger.warning(
                    f"Validation failed for event object (type: MESSAGE_NEW: {event})"  # noqa: E501
                )
                continue

            # --- Commands ---
            if msg.request_text == "/lang":
                continue

            # --- Events ---
            msg_lower = msg.request_text.lower()
            if (msg_lower in [
                "новости",
                "новости города",
                "новости мирного",
                "новости в городе",
                "новости в мирном",
                "события",
                "события города",
                "события мирного",
                "события в городе",
                "события в мирном",
            ]) or (
                (
                    "новости" in msg_lower or
                    "события" in msg_lower
                ) and (
                    "мирном" in msg_lower or
                    "городе" in msg_lower or
                    "мирного" in msg_lower or
                    "города" in msg_lower
                )
            ):
                vk.messages.send(
                    message=create_events_message().response_text,
                    peer_id=message.peer_id,
                    random_id=get_random_id(),
                )
                continue

            # --- Weather ---
            if (msg_lower in [
                "погода",
                "погода в городе",
                "погода в мирном",
                "погода мирного",
                "прогноз погоды",
                "будет ли дождь?",
                "будет ли снег?",
                "будет дождь?",
                "будет снег?",
                "когда дождь?",
                "когда снег?",
                "когда будет дождь?",
                "когда будет снег?",
                "когда потеплеет?",
                "осадки",
                "осадки в городе",
                "осадки город",
                "осадки мирный",
                "осадки в мирном",
            ]) or (
                (
                    (
                        "погода" in msg_lower or
                        "дождь" in msg_lower or
                        "снег" in msg_lower or
                        "солнце" in msg_lower or
                        "ураган" in msg_lower or
                        "буря" in msg_lower or
                        "ветер" in msg_lower or
                        "ветренно" in msg_lower or
                        "осадки" in msg_lower
                    ) and (
                        "мирный" in msg_lower or
                        "город" in msg_lower or
                        "округ" in msg_lower or
                        "регион" in msg_lower
                    )
                )
            ):
                vk.messages.send(
                    message=get_weather_message(msg).response_text,
                    peer_id=message.peer_id,
                    random_id=get_random_id(),
                )
                continue

            # --- ML ---
            answer_msg = query_ml(msg, user_prefs)
            # --- Events ---
            if answer_msg.request_type == MessageRequestType.EVENTS:
                vk.messages.send(
                    message=create_events_message().response_text,
                    peer_id=message.peer_id,
                    random_id=get_random_id(),
                )

            # Normal messages
            vk.messages.send(
                message=answer_msg.response_text,
                peer_id=message.peer_id,
                random_id=get_random_id(),
            )
        else:
            logger.critical(
                f"Other message type: {event.type}"
            )


if __name__ == "__main__":
    run()
