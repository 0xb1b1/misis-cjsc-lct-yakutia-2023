#!/usr/bin/env python3
from pydantic import BaseModel, Field


class CityEventSchema(BaseModel):
    title: str = Field(
        description="Event title",
    )

    description: str = Field(
        description="Event description",
    )

    link: str = Field(
        description="Link to full event page",
    )


class CityEventsSchema(BaseModel):
    events: list[CityEventSchema] = Field(
        description="List of city events parsed at backend startup",
    )
