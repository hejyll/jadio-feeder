from __future__ import annotations

import datetime as dt
from logging import getLogger
from pathlib import Path
from typing import Optional, Union

import tqdm
from bson import ObjectId
from jadio_recorder import Database as RecorderDatabase
from jadio_recorder import RecordedProgram

from .config import Config
from .database import FeederDatabase
from .podcast import PodcastRssFeedGenCreator

logger = getLogger(__name__)


class Feeder:
    def __init__(
        self,
        base_url: str = "http://localhost",
        rss_feed_root: Union[str, Path] = ".",
        media_root: Union[str, Path] = ".",
        feeder_database_host: Optional[str] = None,
        recorder_database_host: Optional[str] = None,
    ) -> None:
        self._base_url = base_url
        self._rss_feed_root = Path(rss_feed_root)
        self._media_root = Path(media_root)

        self._feeder_database = FeederDatabase(feeder_database_host)
        self._recorder_database = RecorderDatabase(recorder_database_host)

    @property
    def feeder_db(self) -> FeederDatabase:
        return self._feeder_database

    @property
    def recorder_db(self) -> RecorderDatabase:
        return self._recorder_database

    def __enter__(self) -> Feeder:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self.feeder_db.close()
        self.recorder_db.close()

    def register_config(self, config: Config) -> None:
        config = config.to_dict()
        res = self.feeder_db.configs.update_one(config, {"$set": config}, upsert=True)
        if res.upserted_id is not None:
            logger.info(f"registered config: {res.upserted_id}\n{config}")

    def update_feed(
        self,
        config: Config,
        config_id: Union[str, ObjectId],
        pretty: bool = True,
    ) -> None:
        # fetch specified recorded programs
        logger.info(f"update RSS feed: {config}")
        query = config.query.to_mongo_format()
        programs = self.recorder_db.recorded_programs.find(query)
        programs = [RecordedProgram.from_dict(program) for program in programs]
        logger.info(f"fetch {len(programs)} program(s)")
        if len(programs) == 0:
            logger.info("find no programs. RSS feed is not created")
            return

        # create FeedGenerator
        feed_generator = PodcastRssFeedGenCreator(
            self._base_url,
            self._media_root,
        ).create(
            programs,
            channel=config.channel,
            sort_by=config.sort_by,
            from_oldest=config.from_oldest,
            remove_duplicates=config.remove_duplicates,
        )

        # save RSS feed file
        rss_feed_path = self._rss_feed_root / f"{str(config_id)}.xml"
        rss_feed_path.parent.mkdir(exist_ok=True)
        feed_generator.rss_file(rss_feed_path, pretty=pretty)
        logger.info(f"save RSS feed to {rss_feed_path}")

    def update_feeds(self, force_update: bool = False) -> None:
        configs = list(self.feeder_db.configs.find({}))
        for config in tqdm.tqdm(configs):
            config_id = config.pop("_id")
            config = Config.from_dict(config)
            if isinstance(config.query.datetime_range, list):
                last_datetime = config.query.datetime_range[1]
                if (
                    last_datetime + dt.timedelta(days=7) < dt.datetime.now()
                    and not force_update
                    and (self._rss_feed_root / f"{str(config_id)}.xml").exists()
                ):
                    logger.info(
                        f"skip updates to RSS feed of completed channels: {config.query}"
                    )
                    continue
            self.update_feed(config, config_id)
