from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time

options = Options()
# options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

base_url = "https://syllabus.hosei.ac.jp/web/web_search_show.php?search=show&nendo=2025&t_mode=sp&sort=admin26_80&gakubueng=AP&gakubu=%E7%90%86%E5%B7%A5%E5%AD%A6%E9%83%A8&template=t4&bunrui57=%E5%BF%9C%E7%94%A8%E6%83%85%E5%A0%B1%E5%B7%A5%E5%AD%A6%E7%A7%91_%E5%AD%A6%E7%A7%91%E5%B0%82%E9%96%80%E7%A7%91%E7%9B%AE&title_h2=%E5%AD%A6%E7%A7%91%E5%B0%82%E9%96%80%E7%A7%91%E7%9B%AE&title_h2_eng=Specialized%20%20subjects%20of%20faculty"
driver.get(base_url)

print("🔄 授業一覧ページにアクセス中...")

urls = []
base_domain = "https://syllabus.hosei.ac.jp"
visited_urls = set()

while True:
    time.sleep(2)  # JS読み込み待機

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # ✅ 日本語の授業リンクを含む <li class="jp"> だけ取得
    jp_list_items = soup.select("ul.normalList01 li.jp")

    count_this_page = 0
    for li in jp_list_items:
        a_tag = li.find("a", href=True)
        if a_tag and "preview.php" in a_tag["href"]:
            full_url = base_domain + "/web/" + a_tag["href"].lstrip("/")
            if full_url not in urls:
                urls.append(full_url)
                count_this_page += 1

    print(f"📄 授業リンク数（このページ）: {count_this_page}")

    # ✅ 次ページへのリンクを探す
    next_button = soup.select_one("div.pagenav_area li.next a")
    if next_button:
        next_href = next_button.get("href")
        next_url = base_domain + next_href
        if next_url in visited_urls:
            print("🔁 ループ検出で停止")
            break
        visited_urls.add(next_url)
        print(f"➡️ 次ページへ: {next_url}")
        driver.get(next_url)
    else:
        print("✅ 次ページなし。終了。")
        break

driver.quit()

# ✅ 保存
with open("syllabus_urls.json", "w", encoding="utf-8") as f:
    json.dump(urls, f, ensure_ascii=False, indent=2)

print(f"✅ 合計 {len(urls)} 件のJPリンクを syllabus_urls.json に保存しました。")

