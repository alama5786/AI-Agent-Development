import asyncio

from day09.agent.mcp_client import *    

async def main():
    # Connect to the MCP server
    client = await connect()

    # Discover available tools on the MCP server
    tools = await discover_tool(client)
    print("Available tools on the MCP server:")
    for tool in tools:
        print(f"- {tool.name}")

    # Execute a tool on the MCP server
    tool_name = "current_time"  # Replace with the desired tool name
    result = await execute_tool(client, tool_name)
    print(f"\nResult of executing:", result.content[0].text)

    # Disconnect from the MCP server
    await disconnect(client)

asyncio.run(main())