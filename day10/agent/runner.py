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

load_dotenv()

async def main():
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
