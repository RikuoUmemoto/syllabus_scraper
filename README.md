# syllabus_scraper
法政大学理工学部応用情報工学科（2025年度）のシラバス情報を自動収集・構造化するためのスクレイピングツールです。

---

## 📁 構成ファイル

| ファイル名 | 説明 |
|------------|------|
| `url_collector.py` | 授業一覧ページをクロールし、すべての日本語ページ (`preview.php`) のURLを収集します。出力先は `syllabus_urls.json`。 |
| `scrape_syllabus_pc.py` | `syllabus_urls.json` 内の各リンクをPCモードで巡回し、授業名・教員名・授業概要・詳細情報などを抽出して `syllabus_2025_full.json` に保存します。 |
| `syllabus_urls.json` | 授業の詳細ページ（日本語）のURLリスト。 |
| `syllabus_2025_full.json` | 授業名、教員名、授業概要、単位数、曜日・時限、授業計画などを含む全授業情報のJSONファイル。 |

---

## ✅ 使用方法

