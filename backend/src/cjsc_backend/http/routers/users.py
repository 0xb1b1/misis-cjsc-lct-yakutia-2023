#!/usr/bin/env python3
"""
This module contains user utils for the project.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from cjsc_backend.http.schemas.user import \
    UserPreferencesSchema

from cjsc_backend.db.databases import \
    backend_db

from cjsc_backend.db.repos.user import \
    UserPreferencesRepo

from cjsc_backend.models.user import \
    UserPreferences, UserLanguagePreference, \
    MessagePlatform

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/users",
    tags=['Users', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

prefs_repo = UserPreferencesRepo(database=backend_db)


@router.get(
    "/get_preferences",
    response_model=UserPreferencesSchema,
)
def translate_message(
    platform: MessagePlatform,
    user_id: str,
):
    prefs = prefs_repo.find_one_by(
        {
            "platform": platform,
            "user_id": user_id,
        }
    )

    if prefs is None:
        logger.debug(
            f"User preferences not found for user \
({platform=}, {user_id=})"
        )
        new_prefs = UserPreferences(
            platform=platform,
            user_id=user_id,
            language=UserLanguagePreference.RU,
        )
        prefs_repo.save(new_prefs)
        return UserPreferencesSchema(
            platform=new_prefs.platform,
            user_id=new_prefs.user_id,
            language=new_prefs.language,
        )

    prefs_schema = UserPreferencesSchema(
        platform=prefs.platform,
        user_id=prefs.user_id,
        language=prefs.language,
    )

    logger.debug(
        f"Returning user preferences: {prefs_schema}"
    )

    return prefs_schema


@router.patch(
    "/set_language",
    response_model=UserPreferencesSchema,
)
def set_language_preference(
    platform: MessagePlatform,
    user_id: str,
    language: UserLanguagePreference,
):
    (prefs_repo
        .get_collection()
        .update_one(
            {
                "platform": platform.value,
                "user_id": user_id,
            },
            {
                "$set": {
                    "language": language.value,
                }
            }
        )
    )  # noqa: E124

    return prefs_repo.find_one_by(
        {
            "platform": platform,
            "user_id": user_id,
        }
    )
