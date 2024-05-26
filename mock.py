#!/usr/bin/env python3
import sys
from collections import defaultdict
from pathlib import Path

import tqdm
from jadio_recorder import Database, RecordedProgram

sys.path.append("src/jadio_podcast")
from podcast import PodcastRssFeed

DEFAULT_BASE_URL = "http://192.168.1.158/"
MONGO_HOST = "mongodb://192.168.1.158:27017/"
MEDIA_ROOT = Path("/data/media")


def main():
    db = Database(MONGO_HOST)
    programs = list(db.recorded_programs.find({}))

    groups = defaultdict(list)
    for program in tqdm.tqdm(programs):
        program = RecordedProgram.from_dict(program)
        groups[program.name].append(program)

    for name, programs in tqdm.tqdm(groups.items()):
        print(f"{name}: {len(programs)}")
        try:
            feed = PodcastRssFeed(programs)
            name = name.replace("/", "_")
            feed.to_rss(DEFAULT_BASE_URL, MEDIA_ROOT, f"{name}.xml")
        except Exception as e:
            import traceback

            traceback.format_exc()
            # print(e)
            print(programs[0])
            raise e


if __name__ == "__main__":
    main()
