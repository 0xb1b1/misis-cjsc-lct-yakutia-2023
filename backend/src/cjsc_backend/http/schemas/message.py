#!/usr/bin/env python3
from pydantic import BaseModel, Field
from datetime import datetime

from cjsc_backend.models.message import \
    MessagePlatform, MessageRequestType


class MessageSchema(BaseModel):
    platform: MessagePlatform = Field(
        default=MessagePlatform.VK,
        description="Platform of the message. Enum field",
    )

    user_id: str = Field(
        description="User's ID on the platform of the message",
    )

    timestamp: datetime = Field(
        default=datetime.utcnow(),
        description="Timestamp of the message",
    )

    request_text: str | None = Field(
        description="Request message text. None if of Response type",
    )

    response_text: str | None = Field(
        description="Response message text. None if of Request type",
    )

    request_type: MessageRequestType | None = Field(
        default=None,
        description="Request type as detected by ML",
    )

    class Config:
        use_enum_values = True
