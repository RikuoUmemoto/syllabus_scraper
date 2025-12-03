import requests
from bs4 import BeautifulSoup
import json
import time
import re

OUTPUT_FILENAME = "syllabus_2025_full_with_code.json"

# URLリストをロード
with open("syllabus_urls.json", encoding="utf-8") as f:
    syllabus_urls = json.load(f)

results = []

# ===========================
#   科目コード抽出
# ===========================
def extract_course_code(soup, detail_table, url):
    """
    科目コード / 授業コードを安定して抽出する。
    優先度:
    (1) attribute テーブル内の「授業コード / 科目コード」
    (2) subjectTable01 内の「授業コード / 科目コード」
    (3) URLの数字 (fallback)
    """

    # --- (1) attribute テーブル優先 ---
    # 例: <td class="item"><span class="jp">授業コード</span></td><td>H4020</td>
    for key, val in detail_table.items():
        if any(kw in key for kw in ["授業コード", "科目コード", "科目番号", "コード"]):
            return val.strip()

    # --- (2) subjectTable01 ---
    table = soup.find("table", class_="subjectTable01")
    if table:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 2:
                key = tds[0].get_text(strip=True)
                val = tds[1].get_text(strip=True)
                if any(kw in key for kw in ["授業コード", "科目コード", "科目番号", "コード"]):
                    return val.strip()

    # --- (3) fallback: URL の数字列 ---
    m = re.search(r"(\d{6,})", url)
    if m:
        return m.group(1)

    return None


# ===========================
#   各テーブル抽出
# ===========================
def extract_detail_table(soup):
    table_data = {}
    detail_table = soup.find("table", class_="attribute")
    if detail_table:
        for row in detail_table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) >= 2:
                key = tds[0].get_text(strip=True)
                val = tds[1].get_text(strip=True)
                table_data[key] = val
    return table_data



def extract_teaching_plan(soup):
    """
    授業計画テーブル (class="schedule") から
    1回ごとの情報を抽出する。

    列構成（PC版想定）:
      0: 回 / No.
      1: methods of teaching
      2: テーマ / Theme
      3: 内容 / Contents
    """
    plan = []
    table = soup.find("table", class_="schedule")
    if not table:
        return plan

    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        # データ行だけを対象（ヘッダ行には td が無いことが多い）
        if len(cols) >= 4:
            week   = cols[0].get_text(strip=True)
            method = cols[1].get_text(strip=True)
            theme  = cols[2].get_text(strip=True)
            # <br> 区切りを改行でつなげる
            content = cols[3].get_text("\n", strip=True)

            # 空行はスキップしてもいい
            if not week and not theme and not content:
                continue

            plan.append({
                "week": week,
                "method": method,
                "theme": theme,
                "content": content,
            })

    return plan



def extract_overview_from_subject_contents(soup):
    """
    <div class="subjectContents">
      <span class="jp">…</span>
      <span class="en">…</span>
    """
    overview_ja, overview_en = None, None
    div = soup.find("div", class_="subjectContents")
    if div:
        jp_span = div.find("span", class_="jp")
        if jp_span:
            jp_texts = [p.get_text(" ", strip=True) for p in jp_span.find_all("p")]
            overview_ja = "\n".join(jp_texts).strip()

        en_span = div.find("span", class_="en")
        if en_span:
            en_texts = [p.get_text(" ", strip=True) for p in en_span.find_all("p")]
            overview_en = "\n".join(en_texts).strip()

    return overview_ja, overview_en


# ===========================
#   概要（日本語）→ key-value 変換
# ===========================
def parse_overview_ja(raw_text):
    items = {}
    current_key = None
    current_val = []

    for line in raw_text.splitlines():
        header = re.match(r"【(.+?)】", line)
        if header:
            if current_key:
                items[current_key] = "\n".join(current_val).strip()
            current_key = header.group(1).strip()
            current_val = [line[header.end():].strip()]
        elif current_key:
            current_val.append(line.strip())

    if current_key:
        items[current_key] = "\n".join(current_val).strip()

    return items


# 日本語 → 英語キー変換（辞書）
jp_to_en_key = {
    "授業の概要と目的（何を学ぶか） / Outline and objectives": "outline",
    "到達目標 / Goal": "goal",
    "授業の進め方と方法 / Method(s)": "method",
    "授業計画 / Schedule": "schedule_note",
    "テキスト（教科書） / Textbooks": "textbooks",
    "参考書 / References": "references",
    "成績評価の方法と基準 / Grading criteria": "grading",
    "その他の重要事項 / Others": "others"
    # 必要に応じてここに追加
}


# ===========================
#   メインループ
# ===========================
for idx, url in enumerate(syllabus_urls):
    url = url.replace("t_mode=sp", "t_mode=pc")
    print(f"🔄 {idx+1}/{len(syllabus_urls)}: {url}")
    # テスト用：1件だけ動かすときは下の条件分岐を起動してbreak
    #if idx > 0:
    #    break

    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # タイトル
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        # 教員名（PC版は最初の h2）
        h2_tags = soup.find_all("h2")
        teacher = h2_tags[0].get_text(strip=True) if len(h2_tags) else None

        # 詳細テーブル（attribute）
        detail_table = extract_detail_table(soup)

        # 概要
        overview_ja, overview_en = extract_overview_from_subject_contents(soup)

        structured_overview = {}
        if overview_ja:
            parsed = parse_overview_ja(overview_ja)
            structured_overview = {
                jp_to_en_key.get(k, k): v
                for k, v in parsed.items()
            }

        # 授業計画
        teaching_plan = extract_teaching_plan(soup)

        # 科目コード（授業コード）
        course_code = extract_course_code(soup, detail_table, url)

        # 完全版レコード
        results.append({
            "url": url,
            "course_code": course_code,
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


# ===========================
#   保存
# ===========================
with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"🎉 完了: {OUTPUT_FILENAME} に完全版を出力しました！")
