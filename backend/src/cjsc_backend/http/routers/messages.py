#!/usr/bin/env python3
"""
This module handles saving message queries to the database.

All queries to ML models are processed via ml (branch ml-master).
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from pymongo.errors import DuplicateKeyError
from collections import deque

from cjsc_backend.http.schemas.message import \
    MessageSchema

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


# {"platform@user_id": <deque maxlen=3>}
chat_history: dict[str, deque] = dict()


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
    return db_message
