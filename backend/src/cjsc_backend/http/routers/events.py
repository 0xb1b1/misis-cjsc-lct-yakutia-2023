#!/usr/bin/env python3
"""
This module contains event utils for the project.
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from cjsc_backend.http.schemas.event import \
    CityEvent, CityEvents

from cjsc_backend.utils.events_parser import \
    parse_events

events = CityEvents(
    events=parse_events(),
)

# See https://fastapi.tiangolo.com/tutorial/bigger-applications/

router = APIRouter(
    prefix="/events",
    tags=['Events', ],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/get_events",
    response_model=CityEvents,
)
def get_city_events():
    return events


@router.post(
    "/reload_events",
)
def reload_city_events():
    global events
    events = CityEvents(
        events=parse_events(),
    )
