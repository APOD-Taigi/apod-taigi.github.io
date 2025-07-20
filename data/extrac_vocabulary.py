import os
import csv
import re
import json

CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content')
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocabulary.csv')
OUTPUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vocabulary.json')

VOCAB_TITLES = ['## 詞彙對照', '## 詞彙學習']

def extract_vocab_from_md(md_path):
    vocabs = []
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()
    in_vocab = False
    for idx, line in enumerate(lines):
        if any(title in line for title in VOCAB_TITLES):
            in_vocab = True
            continue
        if in_vocab:
            if line.strip().startswith('## ') and not any(title in line for title in VOCAB_TITLES):
                break
            if not line.strip() or re.match(r'^\|?\s*漢羅\s*\|\s*POJ\s*\|\s*KIP\s*\|\s*華語\s*\|\s*English\s*\|?$', line) or re.match(r'^\|?-+\|?-+\|?-+\|?-+\|?-+\|?$', line):
                continue
            if line.strip().startswith('|') and line.count('|') >= 6:
                parts = [cell.strip() for cell in line.strip().split('|')[1:-1]]
                if len(parts) == 5:
                    vocabs.append(parts)
    return vocabs

def walk_md_files(content_dir):
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md'):
                yield os.path.join(root, file)

def main():
    vocab_set = set()
    vocab_list = []
    for md_file in walk_md_files(CONTENT_DIR):
        vocabs = extract_vocab_from_md(md_file)
        for vocab in vocabs:
            key = tuple(vocab)
            if key not in vocab_set:
                vocab_set.add(key)
                vocab_list.append(vocab)
    vocab_list.sort(key=lambda x: x[0])  # 依漢羅排序

    # 輸出 CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['漢羅', 'POJ', 'KIP', '華語', 'English'])
        writer.writerows(vocab_list)
    print(f'已彙整 {len(vocab_list)} 筆詞彙到 {OUTPUT_CSV}')

    # 輸出 JSON
    vocab_json = [
        {"漢羅": v[0], "POJ": v[1], "KIP": v[2], "華語": v[3], "English": v[4]}
        for v in vocab_list
    ]
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(vocab_json, f, ensure_ascii=False, indent=2)
    print(f'已同步輸出 {OUTPUT_JSON}')

if __name__ == '__main__':
    main()