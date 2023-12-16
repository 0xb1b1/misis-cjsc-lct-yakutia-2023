#!/usr/bin/env python3
from pydantic import BaseModel
from datetime import datetime
from vk_api.bot_longpoll import VkBotMessageEvent

# datetime.utcfromtimestamp(timestamp)


class VkMessageUser(BaseModel):
    id: int


class VkMessage(BaseModel):
    from_user: VkMessageUser
    timestamp: datetime
    text: str
    peer_id: int


def vk_message_from_event(event: VkBotMessageEvent):
    message_obj = event.object.message
    return VkMessage(
        from_user=VkMessageUser(
            id=message_obj["from_id"],
        ),
        timestamp=datetime.utcfromtimestamp(message_obj["date"]),
        text=message_obj["text"],
        peer_id=message_obj["peer_id"],
    )
