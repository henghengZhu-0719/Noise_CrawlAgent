import json
from agent_service.graph.state import PipelineState
from agent_service.tools.web_scraper import fetch_html
from agent_service.tools.result_parser import parse_result
from agent_service.agents.llm import structured_llm
from agent_service.agents.factory import create_search_agent, create_download_agent
from agent_service.prompts.filter_prompt import FILTER_PROMPT
from agent_service.prompts.extract_prompt import EXTRACT_PROMPT
from agent_service.prompts.download_prompt import DOWNLOAD_PROMPT
from crawl_service.spiders.gdee_eia import run_search_agent


def crawl_node(state: PipelineState):
    url = state["current_url"]
    html_title, html_content = fetch_html(url)
    return {
        "html_title": html_title,
        "html_content": html_content,
        "logs": [f"爬取完成: {url}"],
    }


def filter_node(state: PipelineState):
    messages = [
        {"role": "system", "content": FILTER_PROMPT},
        {"role": "user", "content": f"新闻标题：{state['html_title']}\n新闻内容：{state['html_content']}"},
    ]
    msg = structured_llm.invoke(messages, temperature=0.1)
    result = msg.is_relevant
    print(f"判断结果: {result}")
    return {
        "is_relevant": result,
        "logs": [f"{'相关' if result else '无关，跳过'}: {state['current_url']}"],
    }


async def extract_node(state: PipelineState):
    search_agent = await create_search_agent()
    messages = [
        {"role": "system", "content": EXTRACT_PROMPT},
        {"role": "user", "content": f"新闻标题：\n新闻内容：{state['html_content']}"},
    ]
    msg = await search_agent.ainvoke({"messages": messages})
    raw = msg["messages"][-1].content
    thinking, detail = parse_result(raw)
    print(thinking)
    result = detail[0] if detail else {}
    return {
        "project_detail": result,
        "search_prompt": result.get("项目名称", "") + result.get("市", "") + "环评",
        "logs": ["详情提取完成"],
    }


def search_node(state: PipelineState):
    results = run_search_agent(state["html_title"], state["search_prompt"])
    print(results)
    return {
        "search_result": results or {},
        "logs": [f"{'找到环评' if results else '未找到环评'}: {state['current_url']}"],
    }


async def download_node(state: PipelineState):
    download_agent = create_download_agent()
    messages = [
        {"role": "system", "content": DOWNLOAD_PROMPT},
        {"role": "user", "content": f"环评url：{state['search_result']},项目名称：{state['project_detail']['项目名称']}"},
    ]
    msg = await download_agent.ainvoke({"messages": messages})
    raw = msg["messages"][-1].content

    pdf_info = {}
    if isinstance(raw, list):
        for block in raw:
            if isinstance(block, dict) and block.get("type") == "text":
                try:
                    pdf_info = json.loads(block["text"])
                    break
                except json.JSONDecodeError:
                    pass
    elif isinstance(raw, str):
        try:
            pdf_info = json.loads(raw)
        except json.JSONDecodeError:
            pass

    local_path = pdf_info.get("环评文件下载路径", "")
    print(f"提取后的路径：{local_path}")
    return {
        "downloaded_pdf": pdf_info,
        "logs": [f"PDF 下载完成: {local_path or '未找到'}"],
    }
