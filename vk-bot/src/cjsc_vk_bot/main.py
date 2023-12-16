#!/usr/bin/env python3
import sys
from loguru import logger
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id

from cjsc_vk_bot import config
from cjsc_vk_bot.models.vk_message import vk_message_from_event

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
            vk.messages.send(
                message='Test message',
                peer_id=message.peer_id,
                random_id=get_random_id(),
            )
        else:
            logger.critical(
                f"Other message type: {event.type}"
            )
