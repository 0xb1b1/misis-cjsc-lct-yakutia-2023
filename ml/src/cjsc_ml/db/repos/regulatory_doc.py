#!/usr/bin/env python3
from pydantic_mongo import AbstractRepository
from pymongo.database import Database
# from pymongo import ASCENDING

from cjsc_ml.models.regulatory_doc import \
    RegulatoryDoc


class RegulatoryDocRepo(AbstractRepository[RegulatoryDoc]):
    def __init__(self, database: Database):
        AbstractRepository.__init__(self, database)
        database["regulatory_docs"].create_index("seq_id", unique=True)

    class Meta:
        collection_name = "regulatory_docs"
