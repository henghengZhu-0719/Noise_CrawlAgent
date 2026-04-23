import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "crawl_service.log",
    level: int = logging.INFO,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 30
) -> logging.Logger:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("crawl_service")
    logger.setLevel(level)
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    file_handler = TimedRotatingFileHandler(
        filename=str(log_path / log_file),
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


logger = setup_logging()