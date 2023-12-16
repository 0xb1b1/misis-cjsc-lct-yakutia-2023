#!/usr/bin/env python3
from pydantic import BaseModel, Field
from pydantic_mongo import ObjectIdField


class RegulatoryDoc(BaseModel):
    id: ObjectIdField = None

    seq_id: int = Field(
        ge=0,
        description="Sequential ID of the document, starting from 0",
    )

    url: str = Field(
        description="URL of the article"
    )

    description: str = Field(
        description="Short description of the content"
    )

    content: str = Field(
        description="Content of the regulatory document"
    )
