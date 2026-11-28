"""
tool_manager.py  --  decides WHICH tool to run for a user's message.

Purpose:
    A very simple, rule-based "router": it looks for keywords in the user's text
    and calls the matching tool. This is the first (non-AI) way of tool selection;
    later stages replace it with an LLM that chooses the tool itself.
"""
from tools import get_current_time, roll_dice, generate_password

def execute_tool(user_input):
    """Executes a tool command based on the user's input.

    Returns:
        A result string if a keyword ("time", "dice", "password") matched,
        otherwise None so the caller can fall back to a normal LLM answer.
    """
    # Keyword matching is case-insensitive and checks for substrings.
    if "time" in user_input.lower(): 
        return f"Current Time: {get_current_time()}"
    elif "dice" in user_input.lower():
        return f"Rolling a 6-sided dice: {roll_dice()}"
    elif "password" in user_input.lower():    
        # This tool needs an extra argument, so we ask the user for it.
        length = input("Enter the desired password length: ")
        # isdigit() guards int() against non-numeric input.
        if length.isdigit():
            return f"Generating a random password of length {length}: {generate_password(int(length))}"
        else:
            return "Please enter a valid number for the password length."
    else:
        # No tool matched.
        return None
