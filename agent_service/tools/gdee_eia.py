"""
target：在广东省生态环境厅进行项目建设，寻求其环评文件
1. 确定项目名称 + 其相关信息（最好的格式是项目名称+涉及的区域）
2. 搜索广东省生态环境厅的环评文件
3. 下载环评文件到本地
4. 解析环评文件，提取项目相关信息
5. 存储项目相关信息到数据库
"""

import re
import random
import time
import os
import json
from datetime import datetime
import pandas as pd

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, Browser

# 搜索基础 URL
BASE_URL = "https://search.gd.gov.cn/search/all/160/"


class CrawlGdee:
    def __init__(self, items: list[str] = []):  # ✅ 改为 list[str]
        self.items = items
        # 随机 UA 池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        ]

        self.output_dir = "results/广东省生态环境厅"
        os.makedirs(self.output_dir, exist_ok=True)

        # 进度记录文件
        self.progress_file = os.path.join(self.output_dir, "progress.json")
        self.crawled_projects = self._load_progress()

        # Playwright 相关（延迟初始化）
        self._playwright = None
        self._browser = None
        self._page = None

    def _load_progress(self) -> set:
        """加载已抓取的项目列表"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"读取进度文件失败: {e}")
                return set()
        return set()

    def _save_progress(self, query: str):
        """保存已抓取的关键词"""
        self.crawled_projects.add(query)
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(list(self.crawled_projects), f, ensure_ascii=False, indent=2)

    def _sanitize_filename(self, name: str) -> str:
        """替换文件名中的非法字符，避免路径解析错误"""
        return re.sub(r'[/\\:*?"<>|]', '_', name)

    # Playwright 生命周期
    def start(self):
        """启动 Playwright，创建浏览器实例"""
        ua = random.choice(self.user_agents)
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        context = self._browser.new_context(
            user_agent=ua,
            locale="zh-CN",
            viewport={"width": 1280, "height": 800},
        )
        self._page = context.new_page()

    def stop(self):
        """关闭 Playwright，爬取结束后调用"""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def _build_url(self, query: str, page: int = 1) -> str:
        """
        构造带参数的搜索 URL。
        第 1 页：?keywords=xxx&filterType=localSite
        后续页：?page=N&keywords=xxx&filterType=localSite
        """
        url = f"{BASE_URL}?keywords={query}&filterType=localSite"
        if page > 1:
            url = f"{BASE_URL}?page={page}&keywords={query}&filterType=localSite"
        return url

    # 页面解析
    def _parse_list_item(self, item_el) -> dict:
        """解析单条搜索结果，返回 {title, url}"""
        title_a = item_el.locator("a.title").first
        title_url = title_a.get_attribute("href") or ""
        title_full = title_a.inner_text().strip()

        # 去掉标签前缀
        tag_el = item_el.locator("a.title span.tag-type")
        tag_type = tag_el.first.inner_text().strip() if tag_el.count() else ""
        title = title_full.replace(tag_type, "", 1).strip()

        return {"title": title, "url": title_url}

    def _parse_results(self) -> list[dict]:
        """从当前已加载的页面中解析所有搜索条目"""
        results = []
        items_locator = self._page.locator("#list-body div.list-item")
        for i in range(items_locator.count()):
            parsed = self._parse_list_item(items_locator.nth(i))
            if parsed["url"]:
                results.append(parsed)
        return results

    def _get_total_pages(self) -> int:
        """从当前已加载的页面中读取总页数"""
        page_links = self._page.locator("div.page-list a.item")
        pg_count = page_links.count()
        if pg_count > 0:
            for i in range(pg_count - 1, -1, -1):
                text = page_links.nth(i).inner_text().strip()
                if text == "最后一页":
                    href = page_links.nth(i).get_attribute("href") or ""
                    m = re.search(r'page=(\d+)', href)
                    if m:
                        return int(m.group(1))
                try:
                    return int(text)
                except ValueError:
                    continue
        return 1

    # 核心抓取
    def fetch_one_page(self, query: str, page: int = 1) -> tuple[list[dict], int]:
        """加载单页搜索结果并解析"""
        url = self._build_url(query, page)
        print(f"    → 请求: {url}")

        try:
            self._page.goto(url, wait_until="networkidle", timeout=120000)
            self._page.wait_for_selector("#list-body", timeout=120000)
        except Exception as e:
            raise Exception(f"请求或等待结果容器超时: {e}")

        results = self._parse_results()
        total_pages = self._get_total_pages()

        print(f" 本页 {len(results)} 条，共 {total_pages} 页")
        return results, total_pages

    def fetch_all_pages(self, query: str, max_pages: int = 10) -> list[dict]:
        """翻页抓取所有结果"""
        all_results = []

        results, total_pages = self.fetch_one_page(query, page=1)
        all_results.extend(results)

        total_pages = min(total_pages, max_pages)

        for p in range(2, total_pages + 1):
            time.sleep(random.uniform(1.5, 3.5))
            results, _ = self.fetch_one_page(query, page=p)
            all_results.extend(results)

        print(f"共抓取 {len(all_results)} 条结果")
        return all_results

    # 文件下载
    def download_file(self, url: str, save_path: str) -> bool:
        """下载单个文件到本地"""
        try:
            headers = {"User-Agent": random.choice(self.user_agents)}
            resp = requests.get(url, headers=headers, timeout=30, stream=True)
            resp.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"    ✓ 已下载: {save_path}")
            return True

        except Exception as e:
            print(f"    ✗ 下载失败 [{url}]: {e}")
            return False

    # 保存
    def save_results(self, results: list[dict], filename: str):
        """将结果保存为 JSON 文件"""
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 结果已保存: {path}")

    def run(self):
        """
        遍历所有查询关键词，依次搜索、抓取、保存
        使用 try/finally 确保 Playwright 一定会被关闭
        """
        self.start()
        try:
            for query in self.items:  
                # 断点续传：跳过已抓取的关键词
                if query in self.crawled_projects:
                    print(f"\n[{query}] 已抓取过，跳过...")
                    continue

                try:
                    safe_name = self._sanitize_filename(query)
                    print(f"\n{'='*50}")
                    print(f"[关键词] {query}")

                    results = self.fetch_all_pages(query, max_pages=2)

                    if results:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{safe_name}_{timestamp}.json"
                        self.save_results(results, filename)
                    else:
                        print(f"未找到相关结果: {safe_name}")

                    self._save_progress(query)

                except Exception as e:
                    print(f"    ✗ 抓取 [{query}] 时发生异常，跳过: {e}")
                    continue

        finally:
            self.stop()


# 新增：供 Pipeline extract_node 调用的单次搜索函数
def run_search_agent(title: str, search_prompt: str) -> list[dict]:
    """
    单次搜索入口，供 Pipeline 节点调用。
    :param title:         保留参数，暂未使用
    :param search_prompt: 上游生成的查询关键词，如 "南沙至珠海城际铁路 广东省 环评"
    :return:              搜索结果列表 [{"title": ..., "url": ...}, ...]
    """
    crawler = CrawlGdee(items=[search_prompt])
    crawler.start()
    try:
        results = crawler.fetch_all_pages(search_prompt, max_pages=2)
        return results
    except Exception as e:
        print(f"搜索失败 [{search_prompt}]: {e}")
        return []
    finally:
        crawler.stop()


if __name__ == "__main__":
    # 批量模式：从 CSV 读取关键词列表
    projects = pd.read_csv("/root/myblog/crawl/agent_output.csv")
    queries = projects["query"].dropna().tolist()  
    crawler = CrawlGdee(items=queries)
    crawler.run()
