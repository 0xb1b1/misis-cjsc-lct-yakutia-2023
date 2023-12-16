#!/usr/bin/env python3
from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField
from datetime import datetime
from enum import Enum


class MessagePlatform(str, Enum):
    """
    Platform of the message.
    """
    VK = "vk"
    TG = "tg"


class Message(BaseModel):
    id: ObjectIdField = None

    platform: MessagePlatform = Field(
        default=MessagePlatform.VK,
        description="Platform of the message. Enum field",
    )

    user_id: str = Field(
        description="User's ID on the platform of the message",
    )

    timestamp: datetime = Field(
        default=datetime.now(),
        description="Timestamp of the message",
    )

    request_text: str | None = Field(
        description="Request message text. None if of Response type",
    )

    response_text: str | None = Field(
        description="Response message text. None if of Request type",
    )

    # class Config:
    #     use_enum_values = True
