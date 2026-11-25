from datetime import datetime
from fastmcp import FastMCP
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
    password = ''.join(secrets.choice(characters) for _ in range(12))
    return password


if __name__ == "__main__":
    print ("Starting the Time Server...")
    mcp.run()
