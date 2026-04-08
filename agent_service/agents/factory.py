from langchain.agents import create_agent
from agent_service.agents.llm import llm
from agent_service.agents.mcp_client import get_mcp_tools
from agent_service.tools.web_scraper import gde_web_search
from agent_service.tools.file_downloader import download_file


async def create_search_agent():
    web_search_tools = await get_mcp_tools()
    return create_agent(model=llm, tools=web_search_tools)


def create_download_agent():
    return create_agent(llm, tools=[gde_web_search, download_file])
