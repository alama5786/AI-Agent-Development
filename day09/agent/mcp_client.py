from fastmcp import FastMCP
from fastmcp.client import Client

async def connect():
    """connect to mcp server"""
    client = Client("server.py")
    await client.__aenter__()

    print("Connected to the mcp server.")

    return client

async def disconnect(client):
    """disconnect from mcp server"""
    await client.__aexit__(None, None, None)
    print("Disconnected from the mcp server.")

async def discover_tool(client):
    """discover available tools on the mcp server"""
    tools = await client.list_tools()
    return tools

async def execute_tool(client, tool_name, args=None):
    """execute a tool on the mcp server"""
    if args is None:
        args = {}
    result = await client.call_tool(tool_name, args)
    return result
