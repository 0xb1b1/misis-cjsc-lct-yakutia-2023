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

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/utils",
    tags=['Utilities', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

yt = YandexFreeTranslate(api="ios")

repo = MessageRepo(database=backend_db)


@router.post(
    "/message/translate",
    response_model=MessageSchema,
)
def translate_message(msg: MessageSchema):
    if msg.request_text is not None:
        msg.request_text = yt.translate(
            "sah", "ru",
            msg.request_text,
        )

    if msg.response_text is not None:
        msg.response_text = yt.translate(
            "ru", "sah",
            msg.response_text,
        )

    return msg
