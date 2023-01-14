import re

import click
import markdown
import pendulum
import yaml
from bs4 import BeautifulSoup

from apod import rss


@click.group()
def cli():
    pass


@cli.command()
@click.argument("date")
@click.argument("vocal")
def shownotes(date, vocal):
    d = pendulum.from_format(date, "YYYYMMDD")
    path = f"content/daily/{d.format('YYYY/MM/YYYYMMDD')}.md"
    with open(path) as fp:
        text = fp.read()

    html = markdown.markdown(text)
    soup = BeautifulSoup(html, "html.parser")

    tags_str = [line for line in text.split("\n") if line.startswith("tags")][0]
    tags = [t.strip() for t in tags_str[7:-1].split(",")]

    def find_content(subtitle):
        target = soup.find(text=re.compile(f"\\[{subtitle}\\]"))
        p = target.find_next("p")
        return str(target), p.get_text()

    hanlo_title, hanlo_text = find_content("漢羅")
    hanlo_title = hanlo_title.replace("[漢羅] ", "")
    hanlo_text = hanlo_text.replace("\n", "")

    print(f"{hanlo_title} ft. {vocal} ({date})")
    print(
        f"""
{hanlo_text}

———
這是 NASA Astronomy Picture of the Day ê 台語文 podcast
原文版：https://apod.nasa.gov/
台文版：https://apod.tw/

今仔日 ê 文章：
https://apod.tw/daily/{date}/
影像：
音樂：P!SCO - 鼎鼎
聲優：{vocal}
翻譯：An-Li Tsai (NCU)
原文：https://apod.nasa.gov/apod/ap{date[2:]}.html\n"""
    )

    print(", ".join(set(["台語, Taiwanese, 天文, astronomy, APOD, Taigi"] + tags)))


@cli.command()
@click.argument("date")
def transcript(date):
    d = pendulum.from_format(date, "YYYYMMDD")
    path = f"content/daily/{d.format('YYYY/MM/YYYYMMDD')}.md"
    with open(path) as fp:
        text = fp.read()

    html = markdown.markdown(text)
    soup = BeautifulSoup(html, "html.parser")

    def find_content(subtitle):
        target = soup.find(text=re.compile(f"\\[{subtitle}\\]"))
        p = target.find_next("p")
        return str(target), p.get_text()

    hanlo_title, hanlo_text = find_content("漢羅")
    hanlo_sentences = re.split(r"[。！？]{1}", hanlo_text.replace("\n", ""))
    poj_title, poj_text = find_content("POJ")
    poj_sentences = re.split(r"[. |! |? ]{2}", poj_text.replace("\n", " "))

    print(hanlo_title)
    print(poj_title)
    print()

    for h, p in zip(hanlo_sentences, poj_sentences):
        print(h)
        print(p)
        print()


@cli.command()
def update_podcasts():
    episodes = rss.get_episodes()
    for episode in episodes:
        path = f"content/daily/{episode.date.format('YYYY/MM/YYYYMMDD')}.md"

        # ignore updated post
        with open(path) as fp:
            if "{{< podcast " in fp.read():
                continue

        with open(path) as fp:
            lines = fp.readlines()

        # ignore post without 漢羅
        index_hanlo = -1
        for i, line in enumerate(lines):
            if "[漢羅]" in line:
                index_hanlo = i

        if not index_hanlo:
            continue

        # update post
        new_lines = (
            lines[:index_hanlo]
            + [f'{{{{< podcast "{episode.id}" >}}}}\n', "\n"]
            + lines[index_hanlo:]
        )

        with open(path, "w") as fp:
            meta_start_passed = False
            for line_no, line in enumerate(new_lines):
                if line.startswith("---") and meta_start_passed:
                    categories = yaml.dump(
                        ["podcast"],
                        default_flow_style=True,
                    )
                    vocals = yaml.dump(
                        [episode.vocal],
                        allow_unicode=True,
                        default_flow_style=True,
                    )
                    fp.write(f"categories: {categories}")
                    fp.write(f"vocals: {vocals}")
                elif line.startswith("---") and not meta_start_passed:
                    meta_start_passed = True

                fp.write(line)
