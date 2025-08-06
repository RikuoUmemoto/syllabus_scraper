# Syllabus Scraper (2025)

法政大学理工学部応用情報工学科（2025年度）のシラバス情報を自動収集・構造化するためのスクレイピングツールです。

---

## 📁 構成ファイル

| ファイル名 | 説明 |
|------------|------|
| `url_collector.py` | SPモードの授業一覧ページをクロールし、すべての日本語ページ (`preview.php`) のURLを収集します。出力先は `syllabus_urls.json`。 |
| `scrape_syllabus_pc.py` | `syllabus_urls.json` 内の各リンクをPCモードで巡回し、授業名・教員名・授業概要・詳細情報などを抽出して `syllabus_2025_full.json` に保存します。 |
| `syllabus_urls.json` | 授業の詳細ページ（日本語）のURLリスト。 |
| `syllabus_2025_full.json` | 授業名、教員名、授業概要（日本語・英語）、単位数、曜日・時限、授業計画などを含む全授業情報のJSONファイル。 |

---

## ✅ 使用方法

### 1. URLの収集（SP=SmartPhoneモード一覧ページの巡回）

```bash
python url_collector.py
```

- 対象URL（例）：  
  `https://syllabus.hosei.ac.jp/web/web_search_show.php?search=show&nendo=2025&t_mode=sp&...`
- 各授業の詳細ページへの日本語リンク（`.jp > a[href*='preview.php?']`）のみを回収。
- 出力: `syllabus_urls.json`

---

### 2. 授業データの取得（PCモード詳細ページの解析）

```bash
python scrape_syllabus_pc.py
```

- `syllabus_urls.json` に含まれるURLを1件ずつアクセス。
- PCモードのHTML構造に対応して、次の情報を収集：
  - 授業名
  - 担当教員
  - 授業概要（日本語・英語）
  - 単位数
  - 開講曜日・時限
  - 授業形態
  - 授業計画（週ごとの概要）など
- 出力: `syllabus_2025_full.json`

---

## 🛠 環境

- Python 3.10+
- Google Chrome（※Chromedriverとバージョンを合わせる必要あり）

### 必要ライブラリ

```bash
pip install -r requirements.txt
```

または個別に：

```bash
pip install selenium beautifulsoup4
```

---

## 🔍 注意事項

- 法政大学の公式WebシラバスのHTML構造が変更された場合、CSSセレクタの修正が必要です。
- 本ツールは教育・研究目的にのみ使用してください。
- スクレイピング対象のサーバーに対して過剰なリクエストを送らないように注意してください（`time.sleep()` を使用して間隔を調整しています）。

---

## 📂 出力例

### syllabus_urls.json

```json
[
  "https://syllabus.hosei.ac.jp/web/preview.php?no_id=2513885&nendo=2025&gakubueng=AP&t_mode=pc&radd=...",
  ...
]
```

### syllabus_2025_full.json

```json
[
  {
    "title": "情報通信論",
    "teacher": "田中 太郎",
    "summary_ja": "この授業では〜",
    "summary_en": "This course aims to...",
    "details": {
      "単位": "2",
      "曜日時限": "火曜3限",
      "授業形態": "対面"
    },
    "schedule": [
      { "week": 1, "topic": "導入とガイダンス" },
      { "week": 2, "topic": "通信の基礎" },
      ...
    ]
  },
  ...
]
```

---

