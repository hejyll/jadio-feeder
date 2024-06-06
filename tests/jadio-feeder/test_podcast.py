from jadio_feeder.podcast import ItunesCategory, ItunesType, PodcastChannel


def test_itunes_category_from_dict():
    data = dict(cat="main", sub="sub")
    actual = ItunesCategory.from_dict(data)

    expected = ItunesCategory(cat="main", sub="sub")
    assert actual == expected


def test_itunes_category_from_dict_empty():
    data = dict()
    actual = ItunesCategory.from_dict(data)

    expected = ItunesCategory()
    assert actual == expected


def test_itunes_category_to_dict():
    actual = ItunesCategory(cat="main", sub="sub").to_dict()

    expected = dict(cat="main", sub="sub")
    assert actual == expected


def test_itunes_category_to_dict_empty():
    actual = ItunesCategory().to_dict()

    expected = dict(cat=None, sub=None)
    assert actual == expected


def test_podcast_channel_from_dict_full():
    data = dict(
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
    )
    actual = PodcastChannel.from_dict(data)

    expected = PodcastChannel(
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
    )
    assert actual == expected


def test_podcast_channel_to_dict_full():
    actual = PodcastChannel(
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
    ).to_dict(serialize=True)

    expected = dict(
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
    )
    assert actual == expected
