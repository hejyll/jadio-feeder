# Jadio Feeder: Podcast RSS feed creator for Jadio

## Setup

### Install

```bash
pip install git+https://github.com/hejyll/jadio-feeder
```

### Use Docker

```bash
export DOCKER_BUILDKIT=1
(cd ./docker && docker-compose up -d)
```

## Usage

### CLI

#### Register config to create RSS feed

```bash
jadio-feeder register-config \
    config.yml \
    --database-host=mongodb://localhost:27017/
```

#### Show registerd configs

```bash
jadio-feeder show-configs \
    --database-host=mongodb://localhost:27017/
```

Output a table like the following to stdout.

```
config_id                 query.platform_ids    query.station_ids    query.persons    query.words    query.datetime_range    channel.title
------------------------  --------------------  -------------------  ---------------  -------------  ----------------------  ---------------
6662857195098cff52529a6b                        TBS                                   JUNK                                   JUNK
```

#### Update Podcast RSS feeds

```bash
jadio-feeder update-feeds \
    --base-url=http://localhost \
    --rss-root=./rss \
    --media-root=./media \
    --database-host=mongodb://localhost:27017/
```

RSS feeds will be generated under the directory specified by the `--rss-root` option with the name `<rss-root>/<config-id>.xml`.

For example, if you execute `register-config` and `show-configs` above, you will get `. /rss/6662857195098cff52529a6b.xml`.

<details><summary>Created sample RSS feed</summary><div>

```xml
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">
    <channel>
        <title>JUNK</title>
        <link>https://www.tbsradio.jp/junk/</link>
        <description>All JUNK programs</description>
        <docs>http://www.rssboard.org/rss-specification</docs>
        <generator>python-feedgen</generator>
        <language>ja</language>
        <lastBuildDate>Fri, 07 Jun 2024 04:02:24 +0000</lastBuildDate>
        <itunes:block>no</itunes:block>
        <itunes:image href="https://tbsradio.g.kuroco-img.app/v=1624347703/files/topics/743_ext_18_0.jpg"/>
        <itunes:explicit>no</itunes:explicit>
        <itunes:complete>no</itunes:complete>
        <itunes:type>episodic</itunes:type>
        <item>
            <title>2024/06/06 01:00</title>
            <link>https://www.tbsradio.jp/junk/</link>
            <description>X（旧Twitter）：<a href="https://twitter.com/junk_tbsr" target="_blank"><u>@junk_tbsr</u></a><br> メール：<a href="mailto:fumou@tbs.co.jp"><u>fumou@tbs.co.jp</a></description>
            <guid isPermaLink="false">10032994</guid>
            <enclosure url="http://localhost/media/radiko.jp/TBS/66623ea6a4db94c8b7e311a5/media.m4a" length="42732193" type="audio/x-m4a"/>
            <pubDate>Thu, 06 Jun 2024 01:00:00 +0919</pubDate>
            <itunes:block>no</itunes:block>
            <itunes:image href="https://program-static.cf.radiko.jp/5739ut8z0b.jpg"/>
            <itunes:duration>7200</itunes:duration>
            <itunes:explicit>no</itunes:explicit>
            <itunes:episodeType>full</itunes:episodeType>
        </item>
        <item>
            <title>2024/06/05 01:00</title>
            <link>https://www.tbsradio.jp/junk/</link>
            <description>X（旧Twitter）：<a href="https://twitter.com/junk_tbsr" target="_blank"><u>@junk_tbsr</u></a><br> メール：<a href="mailto:bakusho@tbs.co.jp"><u>bakusho@tbs.co.jp</a></description>
            <guid isPermaLink="false">10027861</guid>
            <enclosure url="http://localhost/media/radiko.jp/TBS/66623e83a4db94c8b7e311a4/media.m4a" length="42920883" type="audio/x-m4a"/>
            <pubDate>Wed, 05 Jun 2024 01:00:00 +0919</pubDate>
            <itunes:block>no</itunes:block>
            <itunes:image href="https://program-static.cf.radiko.jp/pizopy8f8o.png"/>
            <itunes:duration>7200</itunes:duration>
            <itunes:explicit>no</itunes:explicit>
            <itunes:episodeType>full</itunes:episodeType>
        </item>
        ...
    </channel>
</rss>
```

</div></details>

### Python API

TODO

Refer to the scripts in `samples/`.

## License

These codes are licensed under CC0.

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)
