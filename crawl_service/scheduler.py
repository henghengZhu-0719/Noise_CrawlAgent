# APScheduler 定时任务
from apscheduler.schedulers.blocking import BlockingScheduler
from crawl_service.spiders.gd_transport import CrawlHtml

def run_gd_transport_job():
    print("开始执行定时爬虫任务 (广东省交通运输厅)...")
    url_list = ["https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index.html"]
    for i in range(2, 3):
        url_list.append(f"https://td.gd.gov.cn/zwgk_n/jslyxxgk/xmgs/index_{i}.html")
    
    crawler = CrawlHtml()
    crawler.crawl_html(url_list)
    print("定时爬虫任务执行完毕。")

def start_scheduler():
    scheduler = BlockingScheduler()
    # 每天执行一次（你可以根据需要调整 trigger 和参数，比如 'cron', hour=2 等）
    scheduler.add_job(run_gd_transport_job, 'interval', hours=24)
    print("爬虫调度器已启动，将每 24 小时执行一次任务。按 Ctrl+C 退出。")
    
    # 启动时先立即执行一次
    run_gd_transport_job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("爬虫调度器已停止。")

if __name__ == "__main__":
    start_scheduler()
