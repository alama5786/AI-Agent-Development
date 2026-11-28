"""
server.py  --  Stage 8: an MCP (Model Context Protocol) tool server.

Significance:
    MCP is a standard way to expose tools to AI agents over a protocol instead of
    importing Python functions directly. Any MCP client can discover these tools
    (name + docstring description) and call them. The docstrings matter: they are
    what the planner LLM reads to decide which tool to use.
"""
from datetime import datetime
from fastmcp import FastMCP
# The server's display name.
mcp = FastMCP("Time Server")

@mcp.tool()
def current_time():
    """ returns the current date and time in a human-readable format """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def roll_dice():
    """ simulates rolling a dice with the given number of sides """
    import random
    return random.randint(1, 6)

@mcp.tool()
def generate_password():
    """ generates a random password of the specified length """
    import secrets
    import string

    characters = string.ascii_letters + string.digits + string.punctuation
    # 12 secure random characters (length is fixed in this stage).
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return password


# Run the server (stdio transport) when the file is launched; the client below
# starts this file itself as a subprocess.
if __name__ == "__main__":
    print ("Starting the Time Server...")
    mcp.run()
