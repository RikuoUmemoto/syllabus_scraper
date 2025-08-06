import requests
from bs4 import BeautifulSoup
import json
import time
import re

OUTPUT_FILENAME = "syllabus_ap_2025_full.json"

# 全件取得に変更
with open("syllabus_urls.json", encoding="utf-8") as f:
    syllabus_urls = json.load(f)

results = []

def extract_detail_table(soup):
    table_data = {}
    detail_table = soup.find("table", class_="attribute")
    if detail_table:
        for row in detail_table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                table_data[key] = value
    return table_data

def extract_teaching_plan(soup):
    plan = []
    schedule_table = soup.find("table", class_="schedule")
    if schedule_table:
        for row in schedule_table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 3:
                plan.append({
                    "week": cols[0].get_text(strip=True),
                    "theme": cols[1].get_text(strip=True),
                    "content": cols[2].get_text(strip=True)
                })
    return plan

def extract_overview_from_subject_contents(soup):
    overview_ja, overview_en = None, None
    contents_div = soup.find("div", class_="subjectContents")
    if contents_div:
        jp_span = contents_div.find("span", class_="jp")
        if jp_span:
            jp_texts = [p.get_text(" ", strip=True) for p in jp_span.find_all("p") if p.get_text(strip=True)]
            overview_ja = "\n".join(jp_texts)
        en_span = contents_div.find("span", class_="en")
        if en_span:
            en_texts = [p.get_text(" ", strip=True) for p in en_span.find_all("p") if p.get_text(strip=True)]
            overview_en = "\n".join(en_texts)
    return overview_ja, overview_en

def parse_overview_ja(raw_text):
    items = {}
    current_key = None
    current_val = []

    lines = raw_text.splitlines()
    for line in lines:
        header_match = re.match(r"【(.+?)】", line)
        if header_match:
            if current_key:
                items[current_key] = "\n".join(current_val).strip()
            current_key = header_match.group(1).strip()
            current_val = [line[header_match.end():].strip()]
        elif current_key:
            current_val.append(line.strip())

    if current_key:
        items[current_key] = "\n".join(current_val).strip()

    return items

jp_to_en_key = {
    "授業の概要と目的（何を学ぶか） / Outline and objectives": "outline",
    "到達目標 / Goal": "goal",
    "この授業を履修することで学部等のディプロマポリシーに示されたどの能力を習得することができるか（該当授業科目と学位授与方針に明示された学習成果との関連） / Which item of the diploma policy will be obtained by taking this class?": "diploma_policy",
    "授業で使用する言語 / Default language used in class": "language",
    "授業の進め方と方法 / Method(s)": "method",
    "アクティブラーニング（グループディスカッション、ディベート等）の実施 / Active learning in class (Group discussion, Debate.etc.)": "active_learning",
    "フィールドワーク（学外での実習等）の実施 / Fieldwork in class": "fieldwork",
    "授業計画 / Schedule": "schedule_note",
    "授業時間外の学習（準備学習・復習・宿題等） / Work to be done outside of class (preparation, etc.)": "outside_work",
    "テキスト（教科書） / Textbooks": "textbooks",
    "参考書 / References": "references",
    "成績評価の方法と基準 / Grading criteria": "grading",
    "学生の意見等からの気づき / Changes following student comments": "student_feedback",
    "学生が準備すべき機器他 / Equipment student needs to prepare": "equipment",
    "その他の重要事項 / Others": "others"
}

for idx, url in enumerate(syllabus_urls):
    url = url.replace("t_mode=sp", "t_mode=pc")
    print(f"🔄 {idx+1}/{len(syllabus_urls)}: {url}")
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        h2_tags = soup.find_all("h2")
        teacher = h2_tags[0].get_text(strip=True) if len(h2_tags) > 0 else None

        overview_ja, overview_en = extract_overview_from_subject_contents(soup)
        detail_table = extract_detail_table(soup)
        teaching_plan = extract_teaching_plan(soup)

        structured_overview = {}
        if overview_ja:
            parsed = parse_overview_ja(overview_ja)
            structured_overview = {jp_to_en_key.get(k, k): v for k, v in parsed.items()}

        results.append({
            "url": url,
            "title": title,
            "teacher": teacher,
            "overview_structured": structured_overview,
            "overview_en": overview_en,
            "detail_table": detail_table,
            "teaching_plan": teaching_plan
        })

        time.sleep(1)
    except Exception as e:
        print(f"❌ Error at {url}: {e}")
        continue

with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ 完了: {OUTPUT_FILENAME} に保存しました")

