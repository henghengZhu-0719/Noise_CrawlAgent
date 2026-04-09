import asyncio
from crawl_service.spiders.gd_transport import CrawlHtml

def run_gd_transport():
    # 示例调用
    url_list = ["https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index.html"]
    for i in range(2, 3):
        url_list.append(f"https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index_{i}.html")
    crawler = CrawlHtml()
    crawler.crawl_html(url_list)

from crawl_service.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
