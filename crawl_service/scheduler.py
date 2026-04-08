# APScheduler 定时任务
from apscheduler.schedulers.blocking import BlockingScheduler
from crawl_service.spiders.gd_transport import CrawlHtml

def job():
    print("Running scheduled crawling job...")
    # crawler = CrawlHtml()
    # crawler.crawl_html([...])

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', hours=24)
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
