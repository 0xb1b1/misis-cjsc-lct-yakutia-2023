from pydantic_mongo import AbstractRepository
from pymongo.database import Database
from pymongo import ASCENDING

from cjsc_backend.models.message import \
    Message


class MessageRepo(AbstractRepository[Message]):
    def __init__(self, database: Database):
        AbstractRepository.__init__(self, database)

        database["messages"].create_index(
            [
                ("platform", ASCENDING),
                ("user_id", ASCENDING),
            ],
            unique=False,
        )

        # Only one portfolio in one sector inside a user's account
        database["messages"].create_index(
            [
                ("platform", ASCENDING),
                ("user_id", ASCENDING),
                ("timestamp", ASCENDING),
            ],
            unique=True,
        )

    class Meta:
        collection_name = "messages"
