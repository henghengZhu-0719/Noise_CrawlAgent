from langgraph.graph import StateGraph, START, END
from agent_service.graph.state import PipelineState
from agent_service.graph.nodes import crawl_node, filter_node, extract_node, search_node, download_node
from agent_service.graph.conditions import check_is_relevant, check_has_search_result


def build_pipeline():
    builder = StateGraph(PipelineState)

    builder.add_node("crawl", crawl_node)
    builder.add_node("filter", filter_node)
    builder.add_node("extract", extract_node)
    builder.add_node("search", search_node)
    builder.add_node("download", download_node)

    builder.add_edge(START, "crawl")
    builder.add_edge("crawl", "filter")
    builder.add_conditional_edges("filter", check_is_relevant, {
        "continue": "extract",
        "no_result": END,
    })
    builder.add_edge("extract", "search")
    builder.add_conditional_edges("search", check_has_search_result, {
        "continue": "download",
        "no_result": END,
    })
    builder.add_edge("download", END)

    return builder.compile()
