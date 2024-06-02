from __future__ import annotations

import abc
import dataclasses
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import yaml
from jadio.util import to_datetime

from .podcast import PodcastChannel

_BaseType = TypeVar("_BaseType", bound="_Base")


class _Base(abc.ABC, Generic[_BaseType]):

    @classmethod
    @abc.abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> _BaseType: ...

    @classmethod
    def from_json(cls, filename: Union[str, Path]) -> _BaseType:
        with open(str(filename), "r") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, filename: Union[str, Path]) -> _BaseType:
        with open(str(filename), "r") as fh:
            data = yaml.safe_load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, filename: Union[str, Path]) -> _BaseType:
        filename = Path(filename)
        if filename.suffix == ".json":
            return cls.from_json(filename)
        elif filename.suffix in [".yaml", ".yml"]:
            return cls.from_yaml(filename)
        else:
            raise ValueError(f"{filename.suffix} is not supported")


@dataclasses.dataclass
class Query(_Base):
    station_ids: Optional[List[str]] = None
    persons: Optional[List[str]] = None
    words: Optional[List[str]] = None
    datetime_range: Optional[List[dt.datetime]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Query:
        datetime_range = data.get("datetime_range", None)
        if datetime_range:
            if isinstance(datetime_range, (dt.datetime, str)):
                datetime_range = [datetime_range]
            datetime_range = [to_datetime(dt) for dt in datetime_range]
        return cls(
            station_ids=data.get("station_ids", None),
            persons=data.get("persons", None),
            words=data.get("words", None),
            datetime_range=datetime_range,
        )

    def to_dict(self) -> Dict[str, Any]:
        return dict(
            station_ids=self.station_ids,
            persons=self.persons,
            words=self.words,
            datetime_range=list(self.datetime_range),
        )

    def to_mongo_format(self) -> Dict[str, Any]:
        and_conditions = []
        if self.station_ids:
            and_conditions.append({"station_id": {"$in": self.station_ids}})
        if self.persons:
            target_keys = ["performers", "guests"]
            or_conditions = [{key: {"$in": self.persons}} for key in target_keys]
            and_conditions.append({"$or": or_conditions})
        if self.words:
            target_keys = ["name", "description", "information", "episode_name"]
            or_conditions = []
            for key in target_keys:
                or_conditions += [{key: {"$regex": word}} for word in self.words]
            and_conditions.append({"$or": or_conditions})
        if self.datetime_range:
            condition = {"$gte": self.datetime_range[0]}
            if len(self.datetime_range) == 2:
                condition["$lt"] = self.datetime_range[1]
            and_conditions.append({"datetime": condition})
        if not and_conditions:
            return {}
        return {"$and": and_conditions}


@dataclasses.dataclass
class Config(_Base):
    query: Query
    channel: Optional[PodcastChannel] = None
    sort_by: Optional[str] = None,
    from_oldest: bool = False
    remove_duplicates: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Config:
        channel = data.get("channel", None)
        if channel:
            channel = PodcastChannel.from_dict(channel)
        return cls(
            query=Query.from_dict(data["query"]),
            channel=channel,
            sort_by=data.get("sort_by", None),
            from_oldest=data.get("from_oldest", False),
            remove_duplicates=data.get("remove_duplicates", True),
        )
