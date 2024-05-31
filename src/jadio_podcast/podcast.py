from __future__ import annotations

import copy
import datetime as dt
import os
import urllib
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional, Union

import feedgen.entry
import feedgen.feed
import pytz
from jadio_recorder import RecordedProgram
from mutagen import m4a, mp3, mp4

RADIKO_LINK = "https://radiko.jp/"

logger = getLogger(__file__)


def _media_path_to_duration(path: Union[str, Path]) -> int:
    path = Path(path)
    if not path.exists():
        # TODO: remove this debug pass
        return 0
        raise FileNotFoundError()
    if ".mp3" == path.suffix:
        media = mp3.MP3(path)
    elif ".m4a" == path.suffix:
        # NOTE: M4A: Implementation removed. Every operation will raise. Use mp4 instead.
        # https://mutagen.readthedocs.io/en/latest/changelog.html#id28
        # media = m4a.M4A(path)
        media = mp4.MP4(path)
    elif ".mp4" == path.suffix:
        media = mp4.MP4(path)
    else:
        raise ValueError(f"{path.suffix} is not supported file type")
    return media.info.length


def _datetime_to_pub_data(datetime: dt.datetime, zone: str = "Asia/Tokyo") -> str:
    datetime = copy.deepcopy(datetime)
    datetime = datetime.replace(tzinfo=pytz.timezone(zone))
    return datetime.strftime("%a, %d %b %Y %H:%M:%S %z")


def _path_to_enclosure_url(path: Path, path_root: Path, base_url: str) -> str:
    url = os.path.relpath(str(path.absolute()), str(path_root))
    url = urllib.parse.quote(url)
    # TODO: fix join method
    return urllib.parse.urljoin(base_url, "media/" + url)


def _path_to_enclosure_length(path: Path) -> int:
    if not path.exists():
        # TODO: remove this debug pass
        return 0
        raise FileNotFoundError()
    return os.path.getsize(str(path.absolute()))


def _path_to_enclosure_type(path: Path, is_video: bool) -> str:
    if ".mp3" == path.suffix:
        return "audio/mpeg"
    elif ".m4a" == path.suffix:
        return "audio/x-m4a"
    elif ".mp4" == path.suffix:
        return "video/mp4" if is_video else "audio/x-m4a"
    elif ".mov" == path.suffix:
        return "video/quicktime"
    else:
        raise ValueError(f"{path} is unsupported file type")


@dataclass
class Enclosure:
    url: str
    length: Optional[int] = None  # file size in bytes
    type: Optional[str] = None

    @classmethod
    def from_path(
        cls,
        path: Union[str, Path],
        is_video: bool,
        base_url: str,
        media_root: Path,
    ) -> Enclosure:
        path = Path(path)
        return cls(
            url=_path_to_enclosure_url(path, media_root, base_url=base_url),
            length=_path_to_enclosure_length(path),
            type=_path_to_enclosure_type(path, is_video),
        )


class EpisodeType(Enum):
    FULL: str = "full"
    TRAILER: str = "trailer"
    BONUS: str = "bonus"


class ItunesCategory:
    def __init__(self, cat: Optional[str] = None, sub: Optional[str] = None):
        self.cat = cat
        self.sub = sub

    def to_dict(self) -> Optional[Dict[str, str]]:
        if not self.cat:
            return None
        ret = {"cat": self.cat}
        if self.sub:
            ret["sub"] = self.sub
        return ret


class ItunesType(Enum):
    EPISODIC: str = "episodic"
    SERIAL: str = "serial"


@dataclass
class PodcastItem:
    """
    See: https://help.apple.com/itc/podcasts_connect/#/itcb54353390
    """

    # Required tags
    title: str
    enclosure: Enclosure
    guid: str

    # Recommended tags
    pub_date: Optional[dt.datetime] = None
    description: Optional[str] = None
    itunes_duration: Optional[int] = None  # [seconds]
    link: Optional[str] = None
    itunes_image: Optional[str] = None
    itunes_explicit: bool = False

    # Situational tags
    itunes_title: Optional[str] = None
    itunes_episode: Optional[int] = None
    itunes_season: Optional[int] = None
    itunes_episode_type: EpisodeType = EpisodeType.FULL
    podcast_transcript: Optional[str] = None
    itunes_block: bool = False

    @classmethod
    def from_recorded_program(
        cls,
        program: RecordedProgram,
        base_url: str,
        media_root: Path,
    ) -> PodcastItem:
        duration = program.duration or _media_path_to_duration(program.filename)
        return cls(
            title=program.episode_name,
            enclosure=Enclosure.from_path(
                program.filename, program.is_video, base_url, media_root
            ),
            guid=str(program.episode_id),
            pub_date=program.datetime,
            description=program.description,
            itunes_duration=int(duration),
            link=program.url,
            itunes_image=program.image_url,
        )

    def set_feed_entry(self, entry: feedgen.entry.FeedEntry) -> None:
        entry.title(self.title)
        entry.enclosure(
            url=self.enclosure.url,
            length=self.enclosure.length,
            type=self.enclosure.type,
        )
        entry.guid(self.guid, permalink=False)

        if self.pub_date:
            entry.pubDate(_datetime_to_pub_data(self.pub_date))
        entry.description(self.description)
        entry.podcast.itunes_duration(self.itunes_duration)
        entry.link(href=self.link or RADIKO_LINK)
        # WORKAROUND: avoid file format error
        entry.podcast.__itunes_image = self.itunes_image
        entry.podcast.itunes_explicit("yes" if self.itunes_explicit else "no")

        entry.podcast.itunes_title(self.itunes_title)
        entry.podcast.itunes_episode(self.itunes_episode)
        entry.podcast.itunes_season(self.itunes_season)
        entry.podcast.itunes_episode_type(self.itunes_episode_type.value)
        # entry.podcast.itunes_transcript(self.podcast_transcript)
        entry.podcast.itunes_block(self.itunes_block)


@dataclass
class PodcastChannel:
    # Required tags
    title: str
    description: str
    itunes_image: str
    language: str = "ja"
    itunes_category: Optional[ItunesCategory] = None
    itunes_explicit: bool = False

    # Recommended tags
    itunes_author: Optional[str] = None
    link: Optional[str] = None

    # Situational tags
    itunes_title: Optional[str] = None
    itunes_type: ItunesType = ItunesType.EPISODIC
    copyright: Optional[str] = None
    itunes_new_feed_url: Optional[str] = None
    itunes_block: bool = False
    itunes_complete: bool = False

    @classmethod
    def from_recorded_program(
        cls,
        program: RecordedProgram,
    ) -> PodcastChannel:
        description = f"<![CDATA[ {program.station_id}<br>{program.name} ]]>"
        return PodcastChannel(
            title=program.name,
            description=description,
            itunes_image=program.image_url,
            itunes_author=program.station_id,
            link=program.url,
            copyright=program.copyright,
        )

    def to_feed_generator(self) -> feedgen.feed.FeedGenerator:
        ret = feedgen.feed.FeedGenerator()
        ret.load_extension("podcast")

        ret.title(self.title)
        ret.description(self.description)
        # WORKAROUND: avoid file format error
        ret.podcast.__itunes_image = self.itunes_image
        ret.language(self.language)
        if self.itunes_category:
            ret.podcast.itunes_category(self.itunes_category.to_dict())
        ret.podcast.itunes_explicit("yes" if self.itunes_explicit else "no")

        ret.podcast.itunes_author(self.itunes_author)
        ret.link(href=self.link or RADIKO_LINK)

        # ret.podcast.itunes_title(self.itunes_title)
        ret.podcast.itunes_type(self.itunes_type.value)
        ret.copyright(self.copyright)
        ret.podcast.itunes_new_feed_url(self.itunes_new_feed_url)
        ret.podcast.itunes_block(self.itunes_block)
        ret.podcast.itunes_complete(self.itunes_complete)
        return ret


def programs_to_podcast_rss_feed(
    programs: List[RecordedProgram],
    base_url: str,
    media_root: Path,
    remove_duplicated_episodes: bool = True,
    filename: Optional[str] = None,
    pretty: bool = True,
) -> str:
    sort_key = "datetime"
    if len(set(program.station_id for program in programs)) > 1:
        sort_key = "datetime"
    elif programs[0].station_id in ["onsen.ag", "hibiki-radio.jp"]:
        sort_key = "episode_id"
    programs = sorted(programs, key=lambda x: getattr(x, sort_key), reverse=True)

    if remove_duplicated_episodes:
        unique_programs = []
        prev_episode_id = None
        for program in programs:
            if prev_episode_id != program.episode_id:
                unique_programs.append(program)
            prev_episode_id = program.episode_id

    # create channel of RSS feed
    latest_program = programs[0]
    channel = PodcastChannel.from_recorded_program(latest_program)

    # create items of RSS feed
    feed_generator = channel.to_feed_generator()
    for program in programs:
        try:
            item = PodcastItem.from_recorded_program(program, base_url, media_root)
            item.set_feed_entry(feed_generator.add_entry())
        except Exception as err:
            logger.error(f"error: {err}\n{program}", stack_info=True)

    # output RSS feed
    if filename:
        Path(filename).parent.mkdir(exist_ok=True)
        feed_generator.rss_file(filename, pretty=pretty)
        return filename
    return feed_generator.rss_str(pretty=pretty)
