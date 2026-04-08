import requests
import random
import os
from bs4 import BeautifulSoup
from langchain.tools import tool
from agent_service.config import USER_AGENTS


def fetch_html(url: str):
    """从 URL 获取 HTML 内容，返回 (safe_title, text_content)"""
    try:
        response = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "未命名"
        safe_title = "".join(
            c for c in title
            if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '！', '，', '。', '？', '（', '）', '"', '"')
        )
        print(f"成功爬取 {url}，标题: {safe_title}")
        return safe_title, soup.get_text()
    except Exception as e:
        print(f"请求失败: {url} → {e}")
        return None, None


@tool
def gde_web_search(url: str) -> str:
    "根据url搜索网页内容,并返回该页面的全部内容"
    response = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
