"""
mcp_client.py  --  small helper wrapper around the FastMCP client.

Significance:
    Hides the connection details so the agent only needs four simple calls:
    connect -> discover_tool -> execute_tool -> disconnect.
"""
from fastmcp import FastMCP
from fastmcp.client import Client

async def connect():
    """connect to mcp server"""
    # Passing a script path makes FastMCP launch server.py as a subprocess.
    client = Client("server.py")
    # Manually enter the async context manager so the session stays open
    # across multiple calls (closed later in disconnect()).
    await client.__aenter__()

    print("Connected to the mcp server.")

    return client

async def disconnect(client):
    """disconnect from mcp server"""
    # Manually leave the async context (None x3 = no exception info).
    await client.__aexit__(None, None, None)
    print("Disconnected from the mcp server.")

async def discover_tool(client):
    """discover available tools on the mcp server"""
    # Returns tool objects with .name, .description and input schema.
    tools = await client.list_tools()
    return tools

async def execute_tool(client, tool_name, args=None):
    """execute a tool on the mcp server"""
    # Tools with no parameters just get an empty argument dictionary.
    if args is None:
        args = {}
    result = await client.call_tool(tool_name, args)
    return result
