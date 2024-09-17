import glob
import re
from pathlib import Path

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
翻譯：An-Li Tsai (NSYSU)
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
    hanlo_sentences = hanlo_text.split("\n")
    poj_title, poj_text = find_content("POJ")
    poj_sentences = poj_text.split("\n")

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


@cli.command()
def update_vocabularies():
    translations = {}

    for file_path in glob.glob("content/daily/*/*/*.md"):
        if not re.match(r"\d{8}\.md", Path(file_path).name):
            continue
        date = Path(file_path).name.split(".")[0]

        with open(file_path) as fp:
            daily_text = fp.read()

        new_translations = get_translations(daily_text)
        for translation in new_translations:
            key = translation["hanlo"].upper().replace("-", " ")
            if not key:
                continue
            if key in translations:
                translations[key]["dates"].append(date)
                if sorted(translations[key]["dates"])[-1] == date:
                    translations[key]["translation"] = translation
            else:
                translations[key] = {"dates": [date], "translation": translation}

    write_vocabularies(translations)


def get_translations(daily_text):
    result = []
    in_vocab_section = False
    for line in daily_text.split("\n"):
        if line.startswith("## ") and "詞彙學習" in line:
            in_vocab_section = True
            continue
        if "{{% /apod %}}" in line:
            in_vocab_section = False
            break
        if in_vocab_section:
            if line.startswith("|") and len(line.split("|")) == 7:
                hanlo, poj, kip, mandarin, english = line.split("|")[1:6]
                if hanlo.strip() == "漢羅":
                    continue
                if "-" in hanlo:
                    continue
                result.append(
                    {
                        "hanlo": hanlo.strip(),
                        "poj": poj.strip(),
                        "kip": kip.strip(),
                        "mandarin": mandarin.strip(),
                        "english": english.strip(),
                    }
                )

    return result


def write_vocabularies(translations):
    title = f"""---
title: 天文台語詞彙對照表
date: {pendulum.now().format('YYYY-MM-DD')}
publishdate: {pendulum.now().format('YYYY-MM-DDT00:00:00+08:00')}
tags: [天文台語詞彙對照表]
summary: 天文台語詞彙對照表
---

## 【漢羅】POJ／KIP／華語／English
"""
    with open("content/vocabulary.md", "w") as fp:
        fp.write(title)

        for _, value in sorted(translations.items()):
            dates = value["dates"]
            hanlo = value["translation"]["hanlo"]
            poj = value["translation"]["poj"]
            kip = value["translation"]["kip"]
            mandarin = value["translation"]["mandarin"]
            english = value["translation"]["english"]
            post_links = [f"[{date}](https://apod.tw/daily/{date})" for date in dates]
            fp.write(
                f'- 【{hanlo}】{poj}／{kip}／{mandarin}／{english} ({", ".join(post_links)})\n'
            )


@cli.command()
def convert_vocabularies_to_table():
    for file_path in glob.glob("content/daily/*/*/*.md"):
        if not re.match(r"\d{8}\.md", Path(file_path).name):
            continue
        date = Path(file_path).name.split(".")[0]

        with open(file_path) as fp:
            lines = fp.readlines()

        with open(file_path, "w") as fp:
            in_vocab_section = False
            for line in lines:
                if line.startswith("## 詞彙學習") and "漢羅/POJ/KIP/華語/English" in line:
                    in_vocab_section = True
                    fp.write("## 詞彙學習\n\n")
                    fp.write("|漢羅|POJ|KIP|華語|English|\n")
                    fp.write("|-|-|-|-|-|\n")
                    continue
                if "{{% /apod %}}" in line:
                    fp.write("\n")
                    in_vocab_section = False

                if not in_vocab_section:
                    fp.write(line)
                else:
                    if line.startswith("- "):
                        target = line[2:].strip()

                        # 【標誌性】piau-chì-sèng/piau-tsì-sìng/標誌性/iconic
                        hanlo = target.split("【")[1].split("】")[0]
                        translations = target.split("】")[1]
                        if len(translations.split("/")) == 4:
                            poj, kip, mandarin, english = translations.split("/")
                            fp.write(f"|{hanlo}|{poj}|{kip}|{mandarin}|{english}|\n")
                        else:
                            print(f"{date}: {line[2:].strip()}")
                            fp.write(line)
