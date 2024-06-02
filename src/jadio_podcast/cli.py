import argparse
import logging
from collections import defaultdict
from pathlib import Path

import tqdm
from jadio_recorder import Database, RecordedProgram

from .podcast import PodcastRssFeedGenCreator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s: %(message)s"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", type=str, help="Base URL of httpd")
    parser.add_argument(
        "rss_feeds_root", type=Path, help="Output RSS feeds root directory"
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
    parser.add_argument(
        "--leave-duplicates",
        action="store_true",
        help="Leave duplicated programs",
    )
    parser.add_argument(
        "--sort-by",
        type=str,
        choices=[None, "datetime", "episode_id"],
        default=None,
        help="Sort key of programs",
    )
    parser.add_argument(
        "--from-oldest",
        action="store_true",
        help="Sort programs from oldest",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    db = Database(args.database_host)
    programs = list(db.recorded_programs.find({}))

    groups = defaultdict(list)
    for program in tqdm.tqdm(programs):
        program = RecordedProgram.from_dict(program)
        groups[(program.name, program.station_id)].append(program)

    for (name, station_id), programs in tqdm.tqdm(groups.items()):
        name = name.replace("/", "_")
        filename = args.rss_feeds_root / station_id / f"{name}.xml"

        # create FeedGenerator
        feed_generator = PodcastRssFeedGenCreator(
            args.base_url,
            args.media_root,
        ).create(
            programs,
            sort_by=args.sort_by,
            from_oldest=args.from_oldest,
            remove_duplicates=not args.leave_duplicates,
        )

        # save RSS feed file
        Path(filename).parent.mkdir(exist_ok=True)
        feed_generator.rss_file(filename, pretty=True)


if __name__ == "__main__":
    main()
