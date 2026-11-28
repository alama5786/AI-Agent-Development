"""
executor.py  --  the "hands" of the agent: runs a chosen action.

Significance:
    The planner only DECIDES what to do; the executor actually does it by calling
    the tool on the MCP server and returning the result (the "observation")
    that the agent loop stores in state.
"""
from mcp_client import execute_tool

async def execute_action (action, state,client):
    """Run the tool named `action` through the MCP client.

    Args:
        action: tool name chosen by the planner.
        state:  current agent state (unused here, kept so every executor has the
                same signature and could use state for tool arguments later).
        client: connected MCP client.
    Returns:
        The tool's text output, or str(result) if the result has no text content.
    """
    result = await execute_tool(
        client,
        action
    )

    # MCP results carry a list of content blocks; the first holds the text.
    if hasattr(result, "content"):
        if result.content:
            return result.content[0].text
    return str(result)
