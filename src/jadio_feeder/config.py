from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from serdescontainer import BaseContainer

from .podcast import PodcastChannel


@dataclass
class Query(BaseContainer):
    """Class for generating queries to find radio programs registered in MongoDB.

    Attributes:
        platform_ids (list of str): Specify ids of platforms to be searched.
            e.g. "radiko.jp", "onsen.ag" and "hibiki-radio.jp".
        station_ids (list of str): Specify ids of stations to be searched.
            e.g. "TBS".
        persons (list of str): Specify names of personalities or guests to be searched.
        words (list of str): Specify the words to be searched.
            This is used to search for radio titles and description fields.
        datetime_range (list of `dt.datetime`): Specify the datetime range to be searched.
            If only one date is specified, then programs after that date are searched.
    """

    platform_ids: Optional[List[str]] = None
    station_ids: Optional[List[str]] = None
    persons: Optional[List[str]] = None
    words: Optional[List[str]] = None
    datetime_range: Optional[List[dt.datetime]] = None

    def to_mongo_format(self) -> Dict[str, Any]:
        and_conditions = []
        if self.platform_ids:
            and_conditions.append({"platform_id": {"$in": self.platform_ids}})
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


@dataclass
class Config(BaseContainer):
    query: Query
    channel: Optional[PodcastChannel] = None
    sort_by: Optional[str] = None
    from_oldest: bool = False
    remove_duplicates: bool = True

    def custom_types() -> List[Any]:
        """For BaseContainer.from_dict"""
        return [Query, PodcastChannel]

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> Config:
        data.pop("_id", None)
        return super().from_dict(data, **kwargs)
