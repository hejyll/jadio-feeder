import argparse
import logging
from logging import getLogger
from pathlib import Path

from jadio_recorder import Database

from .config import Config
from .podcast import PodcastRssFeedGenCreator, RecordedProgram

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)
logger = getLogger(__file__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", type=str, help="Base URL of httpd")
    parser.add_argument(
        "config", type=Path, help="Input config file path (JSON or YAML)"
    )
    parser.add_argument("rss_feed", type=Path, help="Output RSS feed path (XML)")
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

    # construct config
    config: Config = Config.from_file(args.config)
    logger.info(config.query)
    if config.channel:
        logger.info(config.channel)

    # fetch specified recorded programs
    db = Database(args.database_host)
    programs = db.recorded_programs.find(config.query.to_mongo_format())
    programs = [RecordedProgram.from_dict(program) for program in programs]
    logger.info(f"fetch {len(programs)} program(s)")
    if len(programs) == 0:
        logger.info("RSS feed is not created")
        quit()

    # create FeedGenerator
    feed_generator = PodcastRssFeedGenCreator(
        args.base_url,
        args.media_root,
    ).create(
        programs,
        channel=config.channel,
        sort_by=config.sort_by,
        from_oldest=config.from_oldest,
        remove_duplicates=config.remove_duplicates,
    )

    # save RSS feed file
    args.rss_feed.parent.mkdir(exist_ok=True)
    feed_generator.rss_file(args.rss_feed, pretty=True)
    logger.info(f"save RSS feed to {args.rss_feed}")


if __name__ == "__main__":
    main()
