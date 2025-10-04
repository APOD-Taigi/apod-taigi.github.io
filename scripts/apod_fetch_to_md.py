import requests
from bs4 import BeautifulSoup
import re
import os
from markdownify import markdownify as mdify

SOURCE_MAP = {
    "Image Credit": "影像來源",
    "Video Credit": "影片來源",
    "Illustration Credit": "插圖來源",
    # ...可擴充...
}

IP_RIGHT_MAP = {
    "Copyright": "版權",
    "License": "許可",
    "Processing": "處理",
    # ...可擴充...
}



def fetch_apod_html(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.text

def parse_credit(soup):
    source_type = ""
    source_key_en = ""
    source_link = None
    ip_right_type = ""
    ip_right_key_en = ""
    ip_right_link = None
    refs = {}



    # 處理 author 與 source 的部分
    # 找 <b> 內容以 : 結尾且在 SOURCE_MAP
    b_tag = None
    source_type = ""
    for b in soup.find_all("b"):
        b_text = b.get_text(strip=True)
        for k in SOURCE_MAP:
            if b_text.startswith(k):
                b_tag = b
                source_type = SOURCE_MAP[k]
                break
        if b_tag:
            break
    if not b_tag:
        return "", refs

    # 找到 <center> 父節點
    parent = b_tag
    while parent and parent.name != "center":
        parent = parent.parent
    if not parent:
        return "", refs

    # 用 next_siblings 收集 <b> 之後到 </center> 前的所有內容
    author_html = ""
    for elem in b_tag.next_siblings:
        # 停在 </center>
        if elem == None or (getattr(elem, "name", None) == "center" and elem == parent):
            break
        # 跳過空白
        if isinstance(elem, str) and not elem.strip():
            continue
        # <br> 轉成空白
        if getattr(elem, "name", None) == "br":
            author_html += " "
            continue
        author_html += str(elem)

    # 保留 link，並收集 refs
    soup2 = BeautifulSoup(author_html, "html.parser")
    def replace_text(text):
        for k, v in {**SOURCE_MAP, **IP_RIGHT_MAP}.items():
            text = re.sub(rf'\b{k}\b', v, text)
        return text

    for a in soup2.find_all("a"):
        text = replace_text(a.text.strip())
        url = a.get("href")
        ref_key = re.sub(r'\W+', '_', text)
        refs[ref_key] = url
        a.replace_with(f"[{text}][{ref_key}]")

    # 將所有內容接成一行
    author_1 = replace_text(soup2.get_text(separator="", strip=True))
    author_1 = re.sub(r'\s+', ' ', author_1)  # 多個空白合併成一個空白

    # 保留 markdown link
    for a_md in re.findall(r'\[.*?\]\[.*?\]', str(soup2)):
        author_1 = author_1.replace(a_md.replace('[', '').replace(']', ''), a_md)





    # 1. 找出有符合 source_map 的 <b> 行
    b_tag = None
    for b in soup.find_all("b"):
        b_text = b.get_text(strip=True)
        for k in SOURCE_MAP:
            if b_text.startswith(k):
                b_tag = b
                break
        if b_tag:
            break

    if not b_tag:
        return "", refs

    b_content = b_tag.get_text()
    parent = b_tag.parent
    parent_html = str(parent)
    after_b = parent_html.split(str(b_tag), 1)[-1]

    # 解析 source 與 ip_right
    if "&" in b_content:
        # 例如 "Image Credit & Copyright:"
        left, right = b_content.split("&", 1)
        source_part = left.strip()
        ip_right_part = right.strip()
        # ip_right_part 可能含有冒號
        if ":" in ip_right_part:
            ip_right_part = ip_right_part.split(":", 1)[0].strip()
        # 取得 source_type
        for k in SOURCE_MAP:
            if source_part.startswith(k):
                source_type = SOURCE_MAP.get(k, k)
                source_key_en = k
                break
        # 取得 ip_right_type
        for k in IP_RIGHT_MAP:
            if ip_right_part.startswith(k):
                ip_right_type = IP_RIGHT_MAP.get(k, k)
                ip_right_key_en = k
                break
        # author html
        if ":" in b_content:
            author_html = b_content.split(":", 1)[-1].strip()
        else:
            # fallback: 取 <b> 之後的文字
            author_html = BeautifulSoup(after_b, "html.parser").get_text().strip()
    else:
        # 沒有 &，直接取 source
        left, right = b_content.split(":", 1)
        source_part = left.strip()
        # 取得 source_type
        for k in SOURCE_MAP:
            if source_part.startswith(k):
                source_type = SOURCE_MAP.get(k, k)
                source_key_en = k
                break
        # 取得冒號後的 author
        author_html = right.strip()

    # 尋找 source link
    for a in b_tag.find_all("a"):
        text = a.text.strip()
        if text == source_key_en:
            url = a.get("href")
            ref_key = re.sub(r'\W+', '_', text)
            refs[ref_key] = url
            source_link = ref_key
            break

    # 尋找 ip_right link
    for a in b_tag.find_all("a"):
        text = a.text.strip()
        if (ip_right_type and (text == ip_right_type or (ip_right_key_en and text == ip_right_key_en))):
            url = a.get("href")
            ref_key = re.sub(r'\W+', '_', text)
            refs[ref_key] = url
            ip_right_link = ref_key
            break

    # # 解析 author 與 link
    # author_links = []
    # for a in parent.find_all("a"):
    #     text = a.text.strip()
    #     if text and text not in [source_key_en, ip_right_type] and (not ip_right_key_en or text != ip_right_key_en):
    #         url = a.get("href")
    #         ref_key = re.sub(r'\W+', '_', text)
    #         refs[ref_key] = url
    #         author_links.append(f"[{text}][{ref_key}]")
    # # 再抓 author_html 裡的純文字
    # soup2 = BeautifulSoup(author_html, "html.parser")
    # texts = [t for t in soup2.stripped_strings if t not in [a.text.strip() for a in soup2.find_all("a")]]
    # author_links.extend(texts)
    # if not author_links and author_html:
    #     author_links.append(author_html)
    # author = ", ".join([item for item in author_links if item.strip()])

    # 組合 source
    if source_type:
        if source_link and source_link in refs:
            source = f"[{source_type}][{source_link}]"
        else:
            source = source_type
    else:
        source = ""

    # 組合 ip_right
    if ip_right_type:
        if ip_right_link and ip_right_link in refs:
            ip_right = f"[{ip_right_type}][{ip_right_link}]"
        else:
            ip_right = ip_right_type
    else:
        ip_right = ""

    # 組合 credit 格式
    if source and ip_right:
        credit = f"{source} kah {ip_right}: {author_1}"
    elif source:
        credit = f"{source}: {author_1}"
    else:
        credit = f"{ip_right}: {author_1}"

    return credit, refs

def parse_apod(html):
    soup = BeautifulSoup(html, "html.parser")
    # 1. 標題
    title_tag = soup.find_all("b")[0]
    title = title_tag.text.strip() if title_tag else ""

    # 2. 圖片/影片連結
    img = soup.find("img")
    img_url = "https://apod.nasa.gov/apod/" + img['src'] if img else ""
    video_url = ""
    embed = soup.find("iframe")
    if embed and 'youtube' in embed.get('src', ''):
        video_url = embed['src']

    # 3. Credit session
    credit_md, credit_refs = parse_credit(soup)

    # 4. 解析 special_notice
    # 解析 special_notice
    special_notice_md = ""
    tomorrow_b = None
    for b in soup.find_all("b"):
        if re.search(r"Tomorrow'?s picture", b.text, re.IGNORECASE):
            tomorrow_b = b
            break
    if tomorrow_b:
        parent = tomorrow_b
        while parent and parent.name != "center":
            parent = parent.parent
        if parent:
            html_block = ""
            for elem in parent.children:
                if elem == tomorrow_b:
                    break
                if isinstance(elem, str) and not elem.strip():
                    continue
                html_block += str(elem)
            if html_block.strip():
                special_notice_md = mdify(html_block, heading_style="ATX").strip()
                # 去除 markdown 粗體
                special_notice_md = re.sub(r"\*\*(.+?)\*\*", r"\1", special_notice_md)
                # 若不是以 - 開頭，手動加上
                if special_notice_md and not special_notice_md.lstrip().startswith("-"):
                    special_notice_md = f"\n- {special_notice_md}"

    # 5. Explanation
    explanation_md = ""
    explanation_refs = ""
    explanation_b = None
    for b in soup.find_all("b"):
        if "Explanation" in b.text:
            explanation_b = b
            break

    if explanation_b:   # 如果有找到 Explanation
        # 只抓 explanation <b> 後面第一個段落，遇到粗體 Tomorrow's picture 就停
        expl_html = ""
        sib = explanation_b.next_sibling
        while sib:
            # 停止條件：遇到 <b> Tomorrow's picture </b>
            if getattr(sib, "name", None) == "b" and "Tomorrow's picture" in sib.get_text(strip=True):
                break
            # 停止條件：遇到 <p> <center>
            if isinstance(sib, str) and "<p> <center>" in sib:
                break
            # 因為抓取段落無效，我 comment 掉這些條件
            # 停在遇到 <b> 或其他標籤，且內容有 Tomorrow's picture 就 break
            # if getattr(sib, "name", None) in ("b", "strong") and re.search(r"Tomorrow'?s picture", sib.get_text(strip=True), re.IGNORECASE):
            #     break
            # # 如果是純文字且有 Tomorrow's picture 也要 break
            # if isinstance(sib, str) and re.search(r"Tomorrow'?s picture", sib.strip(), re.IGNORECASE):
            #     break
            # # 遇到 <p> <center> 也 break
            # if isinstance(sib, str) and "<p> <center>" in sib:
            #     break
            # 停止條件：遇到 <p> 並且下一個節點是 <center>
            if getattr(sib, "name", None) == "p" and sib.find_next_sibling() and sib.find_next_sibling().name == "center":
                break
            # 停止條件：遇到 <center> 並且前一個節點是 <p>
            if getattr(sib, "name", None) == "center" and sib.previous_sibling and sib.previous_sibling.name == "p":
                break
            expl_html += str(sib)   # 將當前節點加入 expl_html
            sib = sib.next_sibling  # 移動到下一個兄弟節點
        print(expl_html)
        print('======================')
        
        #     else:
        #         expl_html += str(sib)
        #         sib = sib.next_sibling
        #         continue
        #     # 其他條件都不 break
        #     expl_html += str(sib)
        #     sib = sib.next_sibling
        # # markdown 化，先將相對連結轉為絕對連結
        def abs_link(m):
            url = m.group(1)  # 這是 href 的網址
            text = m.group(2) # 這是 <a> 的顯示文字
            if url.startswith("http"):
                return m.group(0)
            # 若是 apod 內部連結（如 ap210320.html），補上主網址
            if url.startswith("ap") and url.endswith(".html"):
                abs_url = f"https://apod.nasa.gov/apod/{url}"
                return f'[{text}]({abs_url})'
            return m.group(0)
        expl_html = re.sub(r'<a href="([^"]+)">([^<]+)</a>', lambda m: f'<a href="{m.group(1) if m.group(1).startswith("http") else ("https://apod.nasa.gov/apod/" + m.group(1))}">{m.group(2)}</a>' if m.group(1).startswith("ap") and m.group(1).endswith(".html") else m.group(0), expl_html)
        #expl_html = re.sub(r'<a href="([^"]+)">([^<]+)</a>', abs_link, expl_html)
        explanation_md_raw = mdify(expl_html, heading_style="ATX").strip()
        # markdown link 轉為 [text][ref]，並收集 refs
        link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
        refs = {}
        def ref_name(text):
            # 產生唯一 ref 名稱
            return re.sub(r'\W+', ' ', text).strip().replace(' ', '_')
        for m in link_pattern.finditer(explanation_md_raw):
            text, url = m.group(1), m.group(2)
            key = ref_name(text)
            # 若同一 text 多次出現，保留第一個 url
            if key not in refs:
                refs[key] = url
        def replace_link(m):
            text, url = m.group(1), m.group(2)
            key = ref_name(text)
            return f'[{text}][{key}]'
        explanation_md = link_pattern.sub(replace_link, explanation_md_raw)
        # refs 放在文章最後
        explanation_refs = ""
        for key, url in refs.items():
            explanation_refs += f'[{key}]:{url}\n'
        # 合併 credit_refs
        for key, url in credit_refs.items():
            if key not in refs:  # 避免重複
                explanation_refs += f'[{key}]:{url}\n'
    else:
        explanation_md = ""
        explanation_refs = ""

    # 6. Explanation 之後的文章（含連結）
    additional_links = []
    for a in soup.find_all("a"):
        if a.parent and a.parent.name == "p" and "Tomorrow" not in a.text:
            if a['href'].startswith("http"):
                additional_links.append(f"[{a.text}]({a['href']})")

    return {
        "title": title,
        "img_url": img_url,
        "video_url": video_url,
        "credit": credit_md,
        "ip_right": "",
        "author": "",
        "explanation": explanation_md,
        "explanation_refs": explanation_refs,
        "additional_links": additional_links,
        "special_notice": special_notice_md,
    }

def get_date_from_url(url):
    # 例如 ap250619.html -> 2025/06/19, 檔名 20250619.md
    m = re.search(r'ap(\d{2})(\d{2})(\d{2})\.html', url)
    if not m:
        return None, None, None
    year = int(m.group(1))
    year += 2000 if year < 50 else 1900
    month = m.group(2)
    day = m.group(3)
    yyyymmdd = f"{year}{month}{day}"
    return f"{year}/{month}", yyyymmdd, day

def merge_lines(text):
    # 先把多個空行保留為段落分隔
    paragraphs = re.split(r'\n\s*\n', text)
    merged = []
    for p in paragraphs:
        lines = [line.strip() for line in p.splitlines() if line.strip()]
        buf = ""
        for line in lines:
            if buf:
                buf += " " + line
            else:
                buf = line
            # 若以 . ? ! 結尾就換行
            if re.search(r'[.?!]$', buf):
                merged.append(buf)
                buf = ""
        if buf:
            merged.append(buf)
    return '\n'.join(merged)

# filepath: /home/altsai/project/20201228.APOD-taigi/github/apod-taigi.github.io/data/apod_fetch_to_md.py
def to_markdown(data, date_str, yyyymmdd, day):
    template_path = os.path.join(os.path.dirname(__file__), "apod_taigi_template.md")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    publishdate = f"{date_str.replace('/', '-')}-{day}T11:45:00+0800"
    apod_url = f"https://apod.nasa.gov/apod/ap{yyyymmdd[2:]}.html"
    print(f"APOD 網址: {apod_url}")
    print(f"credit for md: {data['credit']}")  # 確認 credit 組合內容

    # 確保 template 有 {credit} 佔位符，且 credit 寫入 md
    md = template.format(
        title=data['title'],
        date=f"{date_str.replace('/', '-')}-{day}",
        publishdate=publishdate,
        hero=data['img_url'] or data['video_url'],
        url=apod_url,
        credit=data['credit'],  # 這裡 credit 會寫入 md
        english="",  # 先留空，稍後插入
        special_notice=data.get("special_notice", ""),
    )
    # 將 explanation 內容插入 ## [English] 段落下，refs 放在文章最後
    lines = md.splitlines()
    out = []
    inserted_hanlo = False
    inserted_english = False

    #for i, line in enumerate(lines):
    for line in lines:
        #out.append(line)
        # 在台文翻譯那行前插入 special_notice
        #if line.strip().startswith("- 台文翻譯") and data.get("special_notice"):
        #    out.append(f"- {data['special_notice']}")
        out.append(line)
        # 自動插入 explanation 到 [漢羅]
        if not inserted_hanlo and line.strip().startswith("## [英文]"):
            out.append("")
            if data['explanation']:
                # 去除 markdown link，只留純文字
                hanlo_text = data['explanation']
                # 去除 markdown link [text](url)
                hanlo_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', hanlo_text)
                # 去除 markdown reference link [text][ref]
                hanlo_text = re.sub(r'\[([^\]]+)\]\[[^\]]+\]', r'\1', hanlo_text)
                # 去除 HTML <a> 標籤
                hanlo_text = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', hanlo_text)
                hanlo_text = merge_lines(hanlo_text)
                out.append(hanlo_text)
            inserted_hanlo = True
        # 也插到 [English]
        if not inserted_english and line.strip().startswith("## [English]"):
            out.append("")
            if data['explanation']:
                english_text = merge_lines(data['explanation'])
                out.append(english_text)
            inserted_english = True
    # refs 放在全文最後
    if data.get("explanation_refs"):
        out.append("")
        out.append(data["explanation_refs"].rstrip())
    md = "\n".join(out)
    return md

def save_markdown(md, date_path, yyyymmdd):
    # 取得專案根目錄（data 的上一層）
    project_root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(project_root)
    outdir = os.path.join(project_root, "content", "daily", date_path)
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"{yyyymmdd}.md")
    if os.path.exists(outfile):
        ans = input(f"{outfile} 已存在，是否要覆蓋？(y/N): ").strip().lower()
        if ans != "y":
            print("已取消儲存。")
            return
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"已儲存 {outfile}")

if __name__ == "__main__":
    # 讓使用者只輸入 6 碼日期
    code = input("請輸入 APOD 日期 6 碼（如 250619）：").strip()
    if not re.match(r'^\d{6}$', code):
        print("格式錯誤，請輸入 6 碼數字")
        exit(1)
    url = f"https://apod.nasa.gov/apod/ap{code}.html"
    print(f"正在抓取 {url} ...")
    html = fetch_apod_html(url)
    data = parse_apod(html)
    date_path, yyyymmdd, day = get_date_from_url(url)
    if not date_path:
        print("網址格式錯誤")
        exit(1)
    # 執行 to_markdown 並印出 md 內容
    md = to_markdown(data, date_path, yyyymmdd, day)
    #print(md)  # <--- 這行會印出產生的 markdown 內容
    save_markdown(md, date_path, yyyymmdd)