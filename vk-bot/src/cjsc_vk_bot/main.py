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

            answer_msg = query_ml(msg, user_prefs).response_text
            # --- Events ---
            if answer_msg.request_type == MessageRequestType.EVENTS:
                vk.messages.send(
                    message=create_events_message(),
                    peer_id=message.peer_id,
                    random_id=get_random_id(),
                )

            # Normal messages
            vk.messages.send(
                message=answer_msg,
                peer_id=message.peer_id,
                random_id=get_random_id(),
            )
        else:
            logger.critical(
                f"Other message type: {event.type}"
            )


if __name__ == "__main__":
    run()
