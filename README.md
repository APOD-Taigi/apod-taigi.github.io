# 逐工一幅天文圖

## Cron Job

- 每天早上兩點會更新 podcast 資料到對應文章
- 每天下午一點會做一次文章重新上架，如果 publishdate 時間到了就會上（手動推到 main 也會上）

## 上稿教學

- 請在 `content/daily` 底下對應日期的資料夾新增檔案，例如 `content/daily/2021/01/20210122.md`
- 參考以下說明填入對應資料

### 格式說明

- 文章使用 Markdown 格式
- Markdown 寫法可參考 [Basic writing and formatting syntax](https://docs.github.com/en/github/writing-on-github/basic-writing-and-formatting-syntax)

底下是範例
```markdown
---
title: 銀河環 # 必填，文章標題
date: 2021-01-22 # 必填，文章日期
publishdate: 2021-01-22T13:00:00+08:00 # 非必填，文章預計上架日期，沒填就會直接上，目前每天下午一點會檢查有沒有要上架的文章
draft: true # 非必填，填了就完全不會上架
tags: [玫瑰星雲, 星團, NGC 2244, 恆星風, 麒麟座] # 必填，幫文章做個小分類
hero: https://apod.nasa.gov/apod/image/2101/MilkyWayRingAlvinWu1024.jpg # 必填，如果是 YouTube 影片會長這樣 https://www.youtube.com/watch?v=M4tdMR5HLtg
summary: 咱 ê 銀河盤面頂，有闊莽莽 ê 宇宙塗粉、恆星、佮星雲。 # 必填，會是首頁文章的說明文字或分享時顯示的文字
---

{{% apod %}}

- 原始文章：[The Milky Ring](https://apod.nasa.gov/apod/ap210122.html) # inline 連結
- 影像提供 kah [版權][copyright]：[Alvin Wu][1] # reference text 連結

## [漢羅]

## [POJ]

## [KIP]

## [English]

## 詞彙學習（台語漢字/POJ/KIP/華語漢字/English）

- 【玫瑰星雲】Mûi-kùi seng-hûn/Mûi-kùi sing-hûn/玫瑰星雲/Rosette Nebula
- 【開放星團】khai-hòng seng-thoân/khai-hòng sing-thuân/開放星團/open cluster

{{% /apod %}}

[copyright]: https://apod.nasa.gov/apod/lib/about_apod.html#srapply
[1]: https://www.instagram.com/alvinwufoto/

```

### 排版規範

- 漢羅排版可參考 [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)
- APOD 很多接在一起的連結，所以連結前後要空格
