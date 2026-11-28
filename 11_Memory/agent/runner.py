"""
runner.py  --  entry point for stage 11: `python runner.py`.

Same as stage 10 plus `create_database()`, which makes sure the SQLite memory
table exists before the agent tries to read or write memories.
"""
from dotenv import load_dotenv
import os
import asyncio
from mcp_client import(
    connect,
    disconnect,
    discover_tool
)
from planner import planner
from executor import execute_action
from loop import run_agent_loop
from answer import format_answer
from memory import create_database

load_dotenv()

async def main():
    # Create memory.db / the `memories` table on first run (no-op afterwards).
    create_database()
    mcp = await connect()
    tools = await discover_tool(mcp)

    print()
    print("Available Tools")
    print("--------------")

    for tool in tools:
        print(tool.name)

    user_request = input("\nUser:")
    state = await run_agent_loop(
        user_request,
        planner,
        execute_action,
        format_answer,
        tools,
        mcp
    )

    print()
    print("Final Answer:")
    print(state["final_answer"])

    await disconnect(mcp)

if __name__ == "__main__":
    asyncio.run(main())
