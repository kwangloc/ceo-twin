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

    while True:
        user_request = input("\nYou> ").strip()
        if not user_request:
            continue
        if user_request.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        start_time = time.perf_counter()
        # user_request = "Why is Project Atlas delayed?"
        # user_request = "Say hi to Loc on Slack and ask if he can help with the Atlas delay."
        # user_request = "Send a message to channel all-vsf-vceo, mention Loc and ask if he can is available for a quick call to discuss the Atlas delay."
        # user_request = "Analyze the project Atlas, figure out why it is delayed and send a message to channel project-atlas, mention Loc and ask if he can help with the Atlas delay."
        # user_request = "Who owns Project V-CEO?"
        # user_request = "Send list of owners for Project V-CEO to channel project-vceo on Slack."
        # user_request = "Gửi danh sách owners của Project V-CEO vào channel project-vceo trên Slack."
        result = await graph.ainvoke(
            {
                "user_request": user_request,
                # Reset only transient fields per user turn.
                # Keep checkpointed history fields (e.g., worker_runs)
                # so follow-up requests can reuse prior results.
                "turn_count": 0,
                "context": [],
                "worker_output": "",
            },
            config=config,
        )
        end_time = time.perf_counter()
        print(f"Workflow completed in {end_time - start_time:.2f} seconds.")
        decision = result["orchestrator_decision"]
        print(f"Last Reasoning: {decision['reasoning']}")
        print(f"Agent: {decision.get('final_response') or decision.get('reasoning', '(none)')}")
        
if __name__ == "__main__":
    asyncio.run(main())
