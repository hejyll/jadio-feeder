#!/usr/bin/env python3
import argparse
import logging
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List

from jadio import Program

from jadio_feeder.config import Config, Query
from jadio_feeder.feeder import Feeder
from jadio_feeder.podcast import ItunesCategory, PodcastChannel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)
logger = getLogger(__file__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url", type=str, default="http://localhost", help="Base URL of httpd"
    )
    parser.add_argument(
        "--rss-root", type=Path, default="/data/rss", help="RSS root directory"
    )
    parser.add_argument(
        "--media-root", type=Path, default="/data/media", help="Media root directory"
    )
    parser.add_argument(
        "--database-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    platform_id = "hibiki-radio.jp"

    with Feeder(
        args.base_url,
        rss_feed_root=args.rss_root,
        media_root=args.media_root,
        feeder_database_host=args.database_host,
        recorder_database_host=args.database_host,
    ) as feeder:

        def find_recorded_programs(query: Query) -> List[Dict[str, Any]]:
            ret = feeder.recorder_db.recorded_programs.find(query.to_mongo_format())
            return list(ret)

        # get all programs of hibiki-radio.jp
        programs = find_recorded_programs(Query(platform_ids=[platform_id]))

        # extract all channel-ids (station-ids) for grouping
        channel_ids = set(program["station_id"] for program in programs)

        for channel_id in channel_ids:
            # fetch target channel's programs
            query = Query(platform_ids=[platform_id], station_ids=[channel_id])
            programs = find_recorded_programs(query)
            if len(programs) == 0:
                return

            # create Podcast channel information
            programs = list(sorted(programs, key=lambda x: x["episode_id"]))
            channel = PodcastChannel.from_program(Program.from_dict(programs[0]))
            # set Podcast category
            # see: https://podcasters.apple.com/support/1691-apple-podcasts-categories
            channel.itunes_category = ItunesCategory(
                cat="Leisure", sub="Animation &amp; Manga"
            )

            # register config for creating RSS feed
            feeder.register_config(Config(query, channel))


if __name__ == "__main__":
    main()
