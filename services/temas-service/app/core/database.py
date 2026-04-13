from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.core.config import get_settings


class MongoManager:
    """Small wrapper around the MongoDB client lifecycle."""

    def __init__(self) -> None:
        self._client: MongoClient | None = None

    def connect(self) -> None:
        if self._client is None:
            settings = get_settings()
            self._client = MongoClient(settings.mongo_uri)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def database(self) -> Database:
        if self._client is None:
            raise RuntimeError("Mongo client is not connected")
        settings = get_settings()
        return self._client[settings.mongo_database]

    def get_collection(self, name: str) -> Collection:
        return self.database[name]


mongo_manager = MongoManager()
