from pymongo import MongoClient
from pymongo.database import Database

from cjsc_backend import config

__all__ = (
    "client",
    "backend_db"
)

client = MongoClient(config.MONGO_URL)

backend_db: Database = (
    client[config.MONGO_BACKEND_DB]
)
