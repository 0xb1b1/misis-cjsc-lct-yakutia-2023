#!/usr/bin/env python3
"""
This module handles queries to the ML model.
"""
from fastapi import APIRouter
from loguru import logger
from pymongo.errors import DuplicateKeyError

from cjsc_ml.http.schemas.message import \
    MessageSchema

from cjsc_ml.db.databases import \
    assets_db

from cjsc_ml.db.repos.regulatory_doc import \
    RegulatoryDocRepo



# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/msg",
    tags=['Messages', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)

regdoc_repo = RegulatoryDocRepo(database=assets_db)


@router.post(
    "/answer",
    response_model=MessageSchema,
)
def generate_response(msg: MessageSchema) -> MessageSchema:
    ...