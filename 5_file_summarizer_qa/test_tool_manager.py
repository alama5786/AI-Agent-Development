# Manual test for tool_manager.execute_tool: run `python test_tool_manager.py`.
# Each keyword should trigger its tool; the last call should print None (no match).
# Note: "password" will prompt for a length on the terminal.
from tool_manager import execute_tool
print (execute_tool("time"))
print (execute_tool("dice"))
print (execute_tool("password"))
print (execute_tool("unknown command"))
