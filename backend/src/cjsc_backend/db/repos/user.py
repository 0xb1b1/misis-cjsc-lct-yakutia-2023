from pydantic_mongo import AbstractRepository
from pymongo.database import Database
from pymongo import ASCENDING

from cjsc_backend.models.user import \
    UserPreferences


class UserPreferencesRepo(AbstractRepository[UserPreferences]):
    def __init__(self, database: Database):
        AbstractRepository.__init__(self, database)

        database["user_preferences"].create_index(
            [
                ("platform", ASCENDING),
                ("user_id", ASCENDING),
            ],
            unique=True,
        )

        # Only one portfolio in one sector inside a user's account
        database["user_preferences"].create_index(
            "language",
            unique=False,
        )

    class Meta:
        collection_name = "user_preferences"
