import re

import feedparser
import pendulum


def get_firstory_ids():
    url = "https://open.firstory.me/rss/user/ckjojbgnfh77i0820urx6iba5"

    firstory_ids = {}
    d = feedparser.parse(url)
    for e in d["entries"]:
        title = e["title"]
        id_ = e["id"]
        type_ = e["itunes_episodetype"]

        # ignore trailer or bonus
        if type_ != "full":
            continue

        # ignore episode without date
        # valid title: NGC 2174 ê 雲山 ft. 阿錕 (20210116)
        finds = re.findall(r".+\(([0-9]{8})\)$", title.strip())
        date = finds[0] if finds else None
        if not date:
            continue
        date = pendulum.from_format(date, "YYYYMMDD", tz="Asia/Taipei")

        firstory_ids[date] = id_

    return firstory_ids
