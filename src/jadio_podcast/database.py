from __future__ import annotations

from typing import Optional

import pymongo
import pymongo.collation
import pymongo.database


class FeederDatabase:
    def __init__(self, host: Optional[str] = None) -> None:
        host = host or "mongodb://localhost:27017/"
        self._client = pymongo.MongoClient(host)

    def __enter__(self) -> FeederDatabase:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @property
    def _database(self) -> pymongo.database.Database:
        return self._client.get_database("podcast")

    @property
    def configs(self) -> pymongo.collation.Collation:
        return self._database.get_collection("configs")
