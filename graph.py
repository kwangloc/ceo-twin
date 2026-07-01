from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from nodes.orchestrator import orchestrator_node
from nodes.retrieval import retrieval_node
from nodes.worker import worker_node
from state import State


def route_after_orchestrator(state: State) -> str:
    return state["next_step"]


builder = StateGraph(State)

builder.add_node("orchestrator", orchestrator_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("worker", worker_node)

builder.add_edge(START, "orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    route_after_orchestrator,
    {
        "retrieve": "retrieval",
        "worker": "worker",
        "end": END,
    },
)

builder.add_edge("retrieval", "worker")
builder.add_edge("worker", "orchestrator")

graph = builder.compile(checkpointer=MemorySaver())