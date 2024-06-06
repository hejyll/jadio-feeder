import datetime as dt

from jadio_feeder.config import Config, Query
from jadio_feeder.podcast import ItunesCategory, ItunesType, PodcastChannel


def test_query_from_dict_datetime_range_2():
    data = dict(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            "2023-01-01",
            "2024-01-01",
        ],
    )
    actual = Query.from_dict(data)

    expected = Query(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
            dt.datetime.fromisoformat("2024-01-01"),
        ],
    )
    assert actual == expected


def test_query_from_dict_datetime_range_1():
    data = dict(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            "2023-01-01",
        ],
    )
    actual = Query.from_dict(data)

    expected = Query(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
        ],
    )
    assert actual == expected


def test_query_to_dict_datetime_range_2():
    actual = Query(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
            dt.datetime.fromisoformat("2024-01-01"),
        ],
    ).to_dict()

    expected = dict(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
            dt.datetime.fromisoformat("2024-01-01"),
        ],
    )
    assert actual == expected


def test_query_to_dict_datetime_range_1():
    actual = Query(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
        ],
    ).to_dict()

    expected = dict(
        station_ids=["station1", "station2"],
        persons=["person1", "person2"],
        words=["word1", "word2"],
        datetime_range=[
            dt.datetime.fromisoformat("2023-01-01"),
        ],
    )
    assert actual == expected


def test_config_from_dict_only_query():
    data = dict(
        query=dict(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                "2023-01-01",
                "2024-01-01",
            ],
        ),
    )
    actual = Config.from_dict(data)

    expected = Config(
        query=Query(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
    )
    assert actual == expected


def test_config_from_dict_full():
    data = dict(
        query=dict(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                "2023-01-01",
                "2024-01-01",
            ],
        ),
        channel=dict(
            title="title",
            description="description",
            itunes_image="http://image.png",
            language="ja",
            itunes_category=dict(cat="main", sub="sub"),
            itunes_explicit=False,
            itunes_author=["author1", "author2"],
            link="http://link.com",
            itunes_title="itunes-title",
            itunes_type="episodic",
            copyright="copyright",
            itunes_new_feed_url="http://link.com/new-feed-url",
            itunes_block=False,
            itunes_complete=False,
        ),
        sort_by=None,
        from_oldest=False,
        remove_duplicates=True,
    )
    actual = Config.from_dict(data)

    expected = Config(
        query=Query(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
        channel=PodcastChannel(
            title="title",
            description="description",
            itunes_image="http://image.png",
            language="ja",
            itunes_category=ItunesCategory(cat="main", sub="sub"),
            itunes_explicit=False,
            itunes_author=["author1", "author2"],
            link="http://link.com",
            itunes_title="itunes-title",
            itunes_type=ItunesType.EPISODIC,
            copyright="copyright",
            itunes_new_feed_url="http://link.com/new-feed-url",
            itunes_block=False,
            itunes_complete=False,
        ),
        sort_by=None,
        from_oldest=False,
        remove_duplicates=True,
    )
    assert actual == expected


def test_config_to_dict_only_query():
    actual = Config(
        query=Query(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
    ).to_dict()

    expected = dict(
        query=dict(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
        channel=None,
        sort_by=None,
        from_oldest=False,
        remove_duplicates=True,
    )
    assert actual == expected


def test_config_to_dict_full():
    actual = Config(
        query=Query(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
        channel=PodcastChannel(
            title="title",
            description="description",
            itunes_image="http://image.png",
            language="ja",
            itunes_category=ItunesCategory(cat="main", sub="sub"),
            itunes_explicit=False,
            itunes_author=["author1", "author2"],
            link="http://link.com",
            itunes_title="itunes-title",
            itunes_type=ItunesType.EPISODIC,
            copyright="copyright",
            itunes_new_feed_url="http://link.com/new-feed-url",
            itunes_block=False,
            itunes_complete=False,
        ),
        sort_by=None,
        from_oldest=False,
        remove_duplicates=True,
    ).to_dict(serialize=True, unserialized_types=[dt.datetime])

    expected = dict(
        query=dict(
            station_ids=["station1", "station2"],
            persons=["person1", "person2"],
            words=["word1", "word2"],
            datetime_range=[
                dt.datetime.fromisoformat("2023-01-01"),
                dt.datetime.fromisoformat("2024-01-01"),
            ],
        ),
        channel=dict(
            title="title",
            description="description",
            itunes_image="http://image.png",
            language="ja",
            itunes_category=dict(cat="main", sub="sub"),
            itunes_explicit=False,
            itunes_author=["author1", "author2"],
            link="http://link.com",
            itunes_title="itunes-title",
            itunes_type="episodic",
            copyright="copyright",
            itunes_new_feed_url="http://link.com/new-feed-url",
            itunes_block=False,
            itunes_complete=False,
        ),
        sort_by=None,
        from_oldest=False,
        remove_duplicates=True,
    )
    assert actual == expected


test_config_from_dict_full()
