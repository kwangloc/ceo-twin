from retrieval.pipeline import retrieve
from state import State


def retrieval_node(state: State) -> dict:
    decision = state["orchestrator_decision"]
    # Fall back to graph + vector + memory if the orchestrator produced no sources
    sources: list[str] = decision.get("retrieval_sources") or ["graph", "vector", "memory"]
    context = retrieve(sources, state["user_request"])
    return {
        "context": context,
        "next_step": "worker",
    }