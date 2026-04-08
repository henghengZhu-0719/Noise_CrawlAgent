# crawl/crawl_list_pages.py
# 职责：爬取50个列表页 → 解析新闻URL → 写入数据库（content暂为空字符串，等详情页爬取后更新）

import random
import time
import sys
from bs4 import BeautifulSoup
from pathlib import Path

# Add project root to sys.path to allow importing backend
import requests
from backend.models.news_urls import NewsURL
from backend.database import SessionLocal


BASE_URL = "https://td.gd.gov.cn"
SOURCE   = "广东省交通运输厅"


class CrawlHtml:

    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        ]
        self.output_dir = Path(f"results/{SOURCE}/list_pages")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _fetch(self, url: str) -> str | None:
        try:
            resp = requests.get(url, headers={
                "User-Agent": random.choice(self.user_agents)
            }, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"请求失败: {url} → {e}")
            return None

    def _parse_news_items(self, html: str) -> list[dict]:
        """解析列表页，提取新闻 URL、标题、日期"""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        ul_tag = soup.find('ul', class_='newList2')
        if not ul_tag:
            return items

        for li in ul_tag.find_all('li'):
            a_tag   = li.find('a')
            date_tag = li.find('span', class_='date')

            if not a_tag or not a_tag.get('href'):
                continue

            href  = a_tag.get('href', '').strip()
            title = a_tag.get_text(strip=True)
            date  = date_tag.get_text(strip=True) if date_tag else ""

            # 补全相对路径
            full_url = href if href.startswith("http") else BASE_URL + href

            items.append({
                "url":   full_url,
                "title": title,
                "date":  date,
            })

        return items

    

    def _save_to_db(self, items: list[dict]) -> tuple[int, int]:
        added, skipped = 0, 0
        db = SessionLocal()  # 直接创建 session

        try:
            existing_urls = {row.url for row in db.query(NewsURL.url).all()}

            for item in items:
                if item["url"] in existing_urls:
                    skipped += 1
                    continue

                db.add(NewsURL(
                    url=item["url"],
                    title=item["title"][:255],
                    content="",
                    is_relevant=None,
                ))
                existing_urls.add(item["url"])
                added += 1
            db.commit()
            return added, skipped

        except Exception as e:
            db.rollback()
            print(f"数据库写入失败: {e}")
            raise

        finally:
            db.close()  # 无论成功失败都释放连接


    def crawl_html(self, url_list: list[str]) -> list[dict]:
        all_results = []

        for idx, url in enumerate(url_list, start=1):
            time.sleep(random.uniform(10, 20))
            print(f"\n[{idx}/{len(url_list)}] 正在处理: {url}")

            html = self._fetch(url)
            if not html:
                continue

            # 保存列表页 HTML（中间产物）
            html_name = url.split('/')[-1]
            (self.output_dir / html_name).write_text(html, encoding="utf-8")

            items = self._parse_news_items(html)
            if not items:
                print(f"未解析到新闻，请检查选择器")
                continue
            print(f"解析到 {len(items)} 条新闻")

            added, skipped = self._save_to_db(items)
            print(f"新增 {added} 条，跳过 {skipped} 条（已存在）")

            all_results.extend(items)

        print(f"\n全部完成，共处理 {len(all_results)} 条新闻 URL")
        return all_results


if __name__ == "__main__":
    url_list = ["https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index.html"]
    for i in range(2, 3):
        url_list.append(f"https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index_{i}.html")

    crawler = CrawlHtml()
    results = crawler.crawl_html(url_list)
    print(results)
