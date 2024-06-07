import argparse
import logging
from logging import getLogger
from pathlib import Path
from typing import Any, Optional

from tabulate import tabulate

from .config import Config
from .feeder import Feeder

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)
logger = getLogger(__file__)


def add_argument_common(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--database-host",
        type=str,
        default="mongodb://localhost:27017/",
        help="MongoDB host",
    )


def add_argument_register_config(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=register_config)
    parser.add_argument("config", type=Path, help="Input config path (JSON or YAML)")


def add_argument_show_configs(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=show_configs)


def add_argument_update_feeds(parser: argparse.ArgumentParser):
    parser.set_defaults(handler=update_feeds)
    parser.add_argument(
        "--base-url", type=str, default="http://localhost", help="Base URL of httpd"
    )
    parser.add_argument(
        "--rss-root", type=Path, default="./rss", help="RSS root directory"
    )
    parser.add_argument(
        "--media-root", type=Path, default="./media", help="Media root directory"
    )


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    name_and_fn_pairs = [
        ("register-config", add_argument_register_config),
        ("show-configs", add_argument_show_configs),
        ("update-feeds", add_argument_update_feeds),
    ]
    for name, add_arument_fn in name_and_fn_pairs:
        sub_parser = subparsers.add_parser(name, help=f"see `{name} -h`")
        add_arument_fn(sub_parser)
        add_argument_common(sub_parser)

    return parser


def register_config(args: argparse.Namespace) -> None:
    config: Config = Config.from_file(args.config)

    with Feeder(
        feeder_database_host=args.database_host,
        recorder_database_host=args.database_host,
    ) as feeder:
        feeder.register_config(config)


def show_configs(args: argparse.Namespace) -> None:
    with Feeder(
        feeder_database_host=args.database_host,
        recorder_database_host=args.database_host,
    ) as feeder:
        table = []
        configs = feeder.feeder_db.configs.find({})
        for config in configs:
            config_id = config.get("_id", None)
            config = Config.from_dict(config)
            query, channel = config.query, config.channel

            datetime_range = query.datetime_range
            if datetime_range:
                datetime_range = tuple(dt.strftime("%Y-%m-%d") for dt in datetime_range)
            else:
                datetime_range = ""

            def pretty_list(x: Optional[Any] = None) -> str:
                return ", ".join(x) if x else ""

            row = {
                "config_id": str(config_id),
                "query.platform_ids": pretty_list(query.platform_ids),
                "query.station_ids": pretty_list(query.station_ids),
                "query.persons": pretty_list(query.persons),
                "query.words": pretty_list(query.words),
                "query.datetime_range": datetime_range,
                "channel.title": channel.title,
            }
            table.append(row)

    table = sorted(
        table, key=lambda x: (x["query.platform_ids"], x["query.station_ids"])
    )
    print(tabulate(table, headers="keys"))


def update_feeds(args: argparse.Namespace) -> None:
    with Feeder(
        args.base_url,
        rss_feed_root=args.rss_root,
        media_root=args.media_root,
        feeder_database_host=args.database_host,
        recorder_database_host=args.database_host,
    ) as feeder:
        feeder.update_feeds()


def main():
    parser = parse_args()
    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
