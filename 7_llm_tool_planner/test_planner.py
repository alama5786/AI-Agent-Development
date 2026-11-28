# Manual test for planner.choose_tool: each request should map to the matching
# tool name (get_current_time, roll_dice, generate_password). Needs a live LLM.
from planner import choose_tool

print(choose_tool("What is the current time?"))
print(choose_tool("Roll a dice for me."))
print(choose_tool("Generate a random password."))
