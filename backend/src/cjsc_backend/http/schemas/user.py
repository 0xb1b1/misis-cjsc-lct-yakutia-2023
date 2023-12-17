#!/usr/bin/env python3
from pydantic import BaseModel, Field


from cjsc_backend.models.user import \
    UserLanguagePreference

from cjsc_backend.models.message import \
    MessagePlatform


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
