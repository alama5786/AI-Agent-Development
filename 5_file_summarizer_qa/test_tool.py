# Manual smoke test for the raw tool functions in tools.py (no LLM involved).
# Run `python test_tool.py` and check that each line prints a sensible value.
from tools import get_current_time, roll_dice, generate_password

print("Current Time:", get_current_time())

print("Rolling a 6-sided dice:", roll_dice())

print("Generating a random password of length 12:", generate_password(12))
