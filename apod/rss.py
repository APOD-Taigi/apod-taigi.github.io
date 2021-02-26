import re
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
        type_ = e["itunes_episodetype"]

        # ignore trailer or bonus
        if type_ != "full":
            continue

        match = re.match(
            r".+ ft. (?P<vocal>\w+) \(((?P<date>[0-9]{8}))\)$", title.strip()
        )
        if match:
            date = pendulum.from_format(
                match.group("date"), "YYYYMMDD", tz="Asia/Taipei"
            )
            vocal = match.group("vocal")
        else:
            raise RuntimeError(f"Invalid Episode Title: {title}")

        episodes.append(Episode(id=id_, title=title, vocal=vocal, date=date))

    return episodes
