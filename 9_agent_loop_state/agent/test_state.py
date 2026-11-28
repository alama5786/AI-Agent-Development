# Manual test of the agent state helpers (no LLM or MCP needed).
# Simulates one loop iteration: create state -> add action -> record observation
# -> next step -> finish, printing the state after each phase.
from state import *

state = create_state (
    "Generate password and tell me current time"
)

print ("initial state")
print (state)

# The planner "chose" generate_password...
add_action(
    state,
    "generate_password"
)

# ...and the executor returned this observation.
record_observation (
    state,
    "generate_password",
    "Password: X#8Lm@4P"
)

next_step (state)

print ("\nState after one Iteration")
print (state)

# Mark the run complete with a final answer.
finish (
    state,
    "Password:X#8Lm@4P\nCurrent Time: 10:35 AM"
)

print ("\nFinal State")
print (state)
