#!/usr/bin/env python3
from pydantic import BaseModel, Field
from enum import Enum

from cjsc_vk_bot.http.schemas.message import \
    MessagePlatform


class UserLanguagePreference(str, Enum):
    RU = "ru"
    SAH = "sah"


class UserPreferencesSchema(BaseModel):
    platform: MessagePlatform = Field(
        description="User's platform",
    )

    user_id: str = Field(
        description="User's ID on the platform",
    )

    language: UserLanguagePreference = Field(
        default=UserLanguagePreference.RU,
        description="User's preferred language",
    )
