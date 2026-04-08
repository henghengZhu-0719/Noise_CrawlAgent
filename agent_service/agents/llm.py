from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel
from agent_service.config import API_KEY, BASE_URL


class FilterResult(BaseModel):
    is_relevant: bool


llm = ChatAnthropic(
    model="MiniMax-M2.7",
    api_key=API_KEY,
    base_url=BASE_URL,
)

structured_llm = llm.with_structured_output(FilterResult)
