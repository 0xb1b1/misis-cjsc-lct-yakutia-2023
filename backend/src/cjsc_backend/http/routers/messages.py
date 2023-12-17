#!/usr/bin/env python3
"""
This module handles saving message queries to the database.

All queries to ML models are processed via ml (branch ml-master).
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from pymongo.errors import DuplicateKeyError
from collections import deque
from datetime import datetime, UTC

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
    prefix="/msg",
    tags=['Messages', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

repo = MessageRepo(database=backend_db)


# {"user_id@platform": <deque maxlen=3>}
chat_history: dict[str, deque[MinifiedMessageSchema]] = dict()


@router.post(
    "/save",
    response_model=MessageSchema,
    description="Save message and return the message obj",
)
def save_message(msg: MessageSchema) -> Message:
    db_message = Message(
        platform=msg.platform,
        user_id=msg.user_id,
        timestamp=msg.timestamp,
        request_text=msg.request_text,
        response_text=msg.response_text,
        request_type=msg.request_type,
    )

    logger.debug(
        f"Saving message to DB: {db_message}",
    )
    try:
        repo.save(db_message)
    except DuplicateKeyError:
        logger.warning(
            f"Duplicate key while saving msg to DB: {db_message}",
        )
        return HTTPException(
            status_code=409,
            detail="This record already exists",
        )

    # Save to chat_history
    chat_history_uid: str = f"{msg.user_id}@{msg.platform.value}"
    if chat_history_uid not in chat_history:
        chat_history[chat_history_uid] = deque(maxlen=6)

    msg.chat_history = None
    chat_history[chat_history_uid].append(
        MinifiedMessageSchema(
            timestamp=msg.timestamp,
            request_text=msg.request_text,
            response_text=msg.response_text,
            request_type=msg.request_type,
        )
    )

    return db_message


@router.get(
    "/history",
    response_model=MessageSchema,
)
def get_history(platform: MessagePlatform, user_id: str):
    """
    Return an empty MessageSchema with populated chat_history.
    """
    chat_history_uid: str = f"{user_id}@{platform.value}"

    if chat_history_uid not in chat_history:
        chat_history_user = []
    else:
        chat_history_user = list(chat_history[chat_history_uid])

    return MessageSchema(
        platform=MessagePlatform.VK,
        user_id="nulltype",
        timestamp=datetime.now(UTC),
        request_text=None,
        response_text=None,
        request_type=MessageRequestType.TRASH,
        chat_history=chat_history_user,
    )
