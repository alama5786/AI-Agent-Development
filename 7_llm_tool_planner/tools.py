"""
tools.py  --  plain Python "tools" the assistant can use.

Purpose:
    A tool is just an ordinary function that does something the LLM cannot do
    reliably on its own (know the real time, generate true randomness, read files...).
    Keeping tools in their own module keeps them testable and reusable.
"""
from datetime import datetime

def get_current_time():
    """Returns the current time as a formatted string.

    Significance: an LLM has no clock; this gives it real, live information.
    Format example: 28-11-2026 03:45:10 PM
    """
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

import random
def roll_dice(sides=6):
    """Simulates rolling a dice with the given number of sides.

    Args:
        sides: number of faces on the dice (default 6).
    Returns:
        A random integer between 1 and `sides` (inclusive).
    """
    return random.randint(1, sides)

import secrets
import string

def generate_password(length=12):
    """Generates a random password of the requested length.

    Uses `secrets` (cryptographically secure) instead of `random`, because
    passwords must not be predictable. Characters come from letters, digits
    and punctuation.
    """

    # Pool of allowed characters (letters + digits + symbols).
    charecters = (string.ascii_letters + string.digits + string.punctuation)

    password=""

    # Pick one random character per position until we reach the requested length.
    for _ in range(length):
        password += secrets.choice(charecters)
    return password


def read_text_file(file_path):
    """Reads the content of a text file and returns it as a string.

    Significance: this is the "file tool" that powers summarize / ask commands.
    Errors are returned as readable strings (not raised) so the assistant keeps
    running and can show the problem to the user.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except Exception as e:
        return f"An error occurred while reading the file: {e}"
