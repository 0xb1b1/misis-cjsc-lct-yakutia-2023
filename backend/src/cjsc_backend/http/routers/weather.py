#!/usr/bin/env python3
"""
This module contains utilities for the project.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from pymongo.errors import DuplicateKeyError
from collections import deque
from datetime import datetime, UTC
from yandexfreetranslate import YandexFreeTranslate

from cjsc_backend.http.schemas.message import \
    MessageSchema, MessagePlatform, \
    MessageRequestType, MinifiedMessageSchema

from cjsc_backend.db.databases import \
    backend_db

from cjsc_backend.db.repos.message import \
    MessageRepo

from cjsc_backend.models.message import \
    Message

from cjsc_backend.utils.weather_parser import \
    create_weather_message

from cjsc_backend.utils.translator import \
    translate

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/weather",
    tags=['Weather', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

repo = MessageRepo(database=backend_db)

weather_text = translate(create_weather_message())


@router.get(
    "/update_weather",
)
def update_weather():
    global weather_text

    weather_text = translate(create_weather_message())


@router.post(
    "/get_weather_message",
    response_model=MessageSchema,
)
def get_weather_message(msg: MessageSchema):
    return MessageSchema(
        platform=msg.platform,
        user_id=msg.user_id,
        timestamp=datetime.now(UTC),
        request_text=None,
        response_text=weather_text,
        request_type=msg.request_type,
    )
