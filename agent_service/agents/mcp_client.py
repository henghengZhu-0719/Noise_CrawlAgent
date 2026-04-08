from langchain_mcp_adapters.client import MultiServerMCPClient
from agent_service.config import DASHSCOPE_API_KEY


async def get_mcp_tools():
    client = MultiServerMCPClient({
        "WebSearch": {
            "transport": "http",
            "url": "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp",
            "headers": {"Authorization": f"Bearer {DASHSCOPE_API_KEY}"},
        }
    })
    return await client.get_tools()
