from dataclasses import dataclass

import feedparser
import pendulum


@dataclass
class Episode:
    id: str
    title: str
    vocal: str
    date: pendulum.DateTime


def get_episodes():
    url = "https://open.firstory.me/rss/user/ckjojbgnfh77i0820urx6iba5"

    episodes = []
    d = feedparser.parse(url)
    for e in d["entries"]:
        title = e["title"]
        id_ = e["id"]

        # FIXME: Get episode from e["itunes_episodetype"] error
        # We need it to ignore episodes whose types are not "full"

        vocal = title.split("ft.")[-1].split("(")[0].strip()
        date = title.split("(")[-1].split(")")[0].strip()
        try:
            date = pendulum.from_format(date, "YYYYMMDD", tz="Asia/Taipei")
        except ValueError:
            continue

        if not (vocal and date):
            raise RuntimeError(f"Invalid Episode Title: {title}")

        episodes.append(Episode(id=id_, title=title, vocal=vocal, date=date))

    return episodes
