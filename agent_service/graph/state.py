from typing_extensions import TypedDict, Annotated
import operator


class PipelineState(TypedDict):
    current_url: str
    html_title: str
    html_content: str
    is_relevant: bool
    project_detail: dict
    search_prompt: str
    search_result: dict
    downloaded_pdf: dict
    logs: Annotated[list[str], operator.add]
