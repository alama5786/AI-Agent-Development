from state import *

state = create_state (
    "Generate password and tell me current time"
)

print ("initial state")
print (state)

add_action(
    state,
    "generate_password"
)

record_observation (
    state,
    "generate_password",
    "Password: X#8Lm@4P"
)

next_step (state)

print ("\nState after one Iteration")
print (state)

finish (
    state,
    "Password:X#8Lm@4P\nCurrent Time: 10:35 AM"
)

print ("\nFinal State")
print (state)