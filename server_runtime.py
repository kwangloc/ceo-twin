from __future__ import annotations

import asyncio
from typing import Any, Literal

from graph import graph
from tools.mcp import initialize_mcp_tools

ConversationRole = Literal["assistant", "director_twin"]

_runtime_lock = asyncio.Lock()
_runtime_ready = False


async def initialize_runtime() -> None:
    global _runtime_ready

    if _runtime_ready:
        return

    async with _runtime_lock:
        if _runtime_ready:
            return

        await initialize_mcp_tools()
        _runtime_ready = True


async def run_query(
    user_request: str,
    thread_id: str,
    role: ConversationRole = "director_twin",
) -> dict[str, Any]:
    await initialize_runtime()

    return await graph.ainvoke(
        {
            "user_request": user_request,
            "conversation_role": role,
            "turn_count": 0,
            "context": [],
            "worker_output": "",
        },
        config={"configurable": {"thread_id": thread_id}},
    )


def extract_final_response(result: dict[str, Any]) -> str:
    decision = result.get("orchestrator_decision") or {}
    final_response = str(decision.get("final_response", "")).strip()
    if final_response:
        return final_response

    reasoning = str(decision.get("reasoning", "")).strip()
    if reasoning:
        return reasoning

    worker_output = str(result.get("worker_output", "")).strip()
    if worker_output:
        return worker_output

    return "I could not produce a response for this turn."