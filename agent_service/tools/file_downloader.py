import requests
import os
from langchain.tools import tool


@tool
def download_file(url: str, project_name: str) -> str:
    """根据url下载文件，保存到本地，并返回本地文件路径，记得添加项目名称"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    os.makedirs("downloads", exist_ok=True)
    file_path = os.path.join("downloads", f"{project_name}.pdf")
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path
