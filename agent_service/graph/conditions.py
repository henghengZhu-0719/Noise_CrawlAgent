from agent_service.graph.state import PipelineState


def check_is_relevant(state: PipelineState):
    return "continue" if state["is_relevant"] else "no_result"


def check_has_search_result(state: PipelineState):
    return "continue" if state["search_result"] else "no_result"
