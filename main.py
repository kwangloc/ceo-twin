import logging
import time
import asyncio
import uuid

logging.getLogger().setLevel(logging.ERROR)

from tools.mcp import initialize_mcp_tools
from graph import graph

async def main():
    # Load MCP tools once
    print("Initializing MCP tools...")
    await initialize_mcp_tools()

    # Run the graph workflow with a unique thread ID
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Running workflow with thread_id: {thread_id}")

    start_time = time.perf_counter()
    result = await graph.ainvoke(
        # {"user_request": "Why is Project Atlas delayed?"},
        # {"user_request": "Say hi to Loc on Slack and ask if he can help with the Atlas delay."},
        # {"user_request": "Send a message to channel all-vsf-vceo, mention Loc and ask if he can is available for a quick call to discuss the Atlas delay."},
        # {"user_request": "Analyze the project Atlas, figure out why it is delayed and send a message to channel project-atlas, mention Loc and ask if he can help with the Atlas delay."},
        # {"user_request": "Who owns Project V-CEO?"},
        # {"user_request": "Send list of owners for Project V-CEO to channel project-vceo on Slack."},
        # {"user_request": "Gửi danh sách owners của Project V-CEO vào channel project-vceo trên Slack."},
        {"user_request": "Due Date triển khai Neo4j staging cho Project V-CEO là ngày nào?"},
        {"user_request": "Gửi tin nhắn để nhắc due date Neo4j staging cho Project V-CEO vào nhóm slack project-v-ceo."},
        config=config,
    )
    end_time = time.perf_counter()
    print(f"Workflow completed in {end_time - start_time:.2f} seconds.")
    return result


if __name__ == "__main__":
    result = asyncio.run(main())

    decision = result["orchestrator_decision"]
    print("=== ORCHESTRATOR DECISION ===")
    print(f"Worker:    {decision['worker_type']}")
    print(f"Should end: {decision.get('should_end')}")
    print(f"Retrieval: {decision['need_retrieval']} → sources: {decision.get('retrieval_sources', [])}")
    print(f"Reasoning: {decision['reasoning']}")

    print("\n=== WORKER RUNS ===")
    runs = result.get("worker_runs", [])
    if not runs:
        print("(none)")
    else:
        for i, run in enumerate(runs, start=1):
            print(f"{i}. worker={run.get('worker')} addons={run.get('addon_skills', [])}")

    print("\n=== FINAL RESPONSE ===")
    print(decision.get("final_response") or decision.get("reasoning", "(none)"))