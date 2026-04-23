import asyncio
from crawl_service.spiders.gd_transport import CrawlHtml

from crawl_service.scheduler import start_scheduler

if __name__ == "__main__":
    start_scheduler()
