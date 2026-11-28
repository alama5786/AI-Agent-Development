"""
runner.py  --  entry point for stage 9: `python runner.py`.

Wires everything together: connect to the MCP server, discover tools, read the
user's request, run the agent loop, print the final answer, disconnect.
"""
from openai import OpenAI
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

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def format_answer (state):
    """Turn the collected actions/observations into a natural-language reply.

    Called by the loop when the planner returns FINISH.
    """
    prompt = f"""
    The user asked:
    {state["user_request"]}
    Actiion performed:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Answer the user naturally.
    Do not mention internal planning.
    Do not mention state.
    Do not mention tools.
    """

    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()

async def main():
    # Connect and discover what tools the server offers.
    mcp = await connect()
    tools = await discover_tool(mcp)

    print()
    print("Available Tools")
    print("--------------")

    for tool in tools:
        print(tool.name)

    # Run the agent on one request and show the result.
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
