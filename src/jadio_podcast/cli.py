import argparse
import logging
from logging import getLogger
from pathlib import Path

from .config import Config
from .feeder import Feeder

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)
logger = getLogger(__file__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", type=str, help="Base URL of httpd")
    parser.add_argument("config", type=Path, help="Input config path (JSON or YAML)")
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

    config: Config = Config.from_file(args.config)

    with Feeder(
        args.base_url,
        rss_feed_root=args.rss_feed.parent,
        media_root=args.media_root,
        feeder_database_host=args.database_host,
        recorder_database_host=args.database_host,
    ) as feeder:
        feeder.update_feed(config, args.rss_feed.stem)


if __name__ == "__main__":
    main()
