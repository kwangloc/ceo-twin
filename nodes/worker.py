from state import State
from workers.catalog import WORKER_CATALOG
from workers.factory import build_worker_agent
from workers.specs import WorkerRuntime


def _content_to_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
            else:
                parts.append(str(item))
        return "\n".join(p for p in parts if p)
    return str(value)


async def worker_node(state: State) -> dict:
    worker_type = state["current_worker_type"]
    spec = WORKER_CATALOG[worker_type]

    runtime = WorkerRuntime(
        model_ref=state.get("model_override"),
        prompt_override=state.get("prompt_override"),
        # Preloaded skills are fixed in WORKER_CATALOG; orchestrator controls add-ons only.
        preloaded_skills=(),
        addon_skills=tuple(state.get("current_addon_skills", [])),
    )

    agent = build_worker_agent(spec, runtime)

    context = state.get("context", [])
    context_text = "\n".join(context) if context else "(none)"
    worker_task = state.get("current_worker_task", "").strip()
    if not worker_task:
        worker_task = "Handle the next best step for this worker role."

    prior_runs = state.get("worker_runs", [])
    prior_runs_text = "\n".join(
        f"- {r.get('worker', '?')}: {_content_to_text(r.get('output', ''))[:400]}"
        for r in prior_runs[-3:]
    ) or "(none)"

    # create_agent returns a dict with "messages".
    # No thread_id/config needed: the worker runs single-turn inside the outer graph;
    # persistent memory is handled by the outer MemorySaver checkpointer.
    result = await agent.ainvoke({
        "messages": [
            {
                "role": "user",
                "content": (
                    "Execution brief from orchestrator (THIS TURN ONLY):\n"
                    f"{worker_task}\n\n"
                    "Original director request (background only):\n"
                    f"{state['user_request']}\n\n"
                    "Completed worker outputs (for deduplication):\n"
                    f"{prior_runs_text}\n\n"
                    "Retrieved context:\n"
                    f"{context_text}\n\n"
                    "Important: complete only the execution brief for this turn. "
                    "Do not redo already completed tasks."
                ),
            }
        ]
    })

    output = _content_to_text(result["messages"][-1].content)
    worker_runs = list(state.get("worker_runs", []))
    worker_runs.append(
        {
            "worker": worker_type,
            "addon_skills": list(state.get("current_addon_skills", [])),
            "output": output,
        }
    )

    return {
        "worker_output": output,
        "worker_runs": worker_runs,
    }