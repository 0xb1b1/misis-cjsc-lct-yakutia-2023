#!/usr/bin/env python3
from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField
from enum import Enum

from cjsc_backend.models.message import \
    MessagePlatform


class UserLanguagePreference(str, Enum):
    RU = "ru"
    SAH = "sah"


class UserPreferences(BaseModel):
    id: ObjectIdField = None

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
