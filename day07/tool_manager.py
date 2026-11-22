from tools import get_current_time, roll_dice, generate_password

def execute_tool(user_input):
    """Executes a tool command based on the user's input."""
    if "time" in user_input.lower(): 
        return f"Current Time: {get_current_time()}"
    elif "dice" in user_input.lower():
        return f"Rolling a 6-sided dice: {roll_dice()}"
    elif "password" in user_input.lower():    
        length = input("Enter the desired password length: ")
        if length.isdigit():
            return f"Generating a random password of length {length}: {generate_password(int(length))}"
        else:
            return "Please enter a valid number for the password length."
    else:
        return None