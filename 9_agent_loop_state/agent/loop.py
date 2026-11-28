"""
loop.py  --  the agent loop (stage 9): PLAN -> ACT -> OBSERVE -> repeat.

Significance:
    This is what turns a single LLM call into an agent. Each iteration the planner
    looks at the state and picks a tool (or FINISH); we run it, record the result,
    and loop again until the planner says FINISH or max_steps is reached.
"""
from state import *

async def run_agent_loop (
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):
    """Run the agent until it finishes.

    Args:
        user_request:   the user's text.
        planner:        function(state, tools) -> tool name or "FINISH".
        execute_action: async function(action, state, client) -> observation.
        format_answer:  function(state) -> final natural-language answer.
        tools:          tool objects discovered from the MCP server.
        client:         connected MCP client.
    Returns:
        The final state dict (contains "final_answer").
    """
    state = create_state (user_request)

    #while can_continue: "This is the heart of our agent"

    while can_continue(state):

    # The planner decide what to do next
        action = planner(state, tools)
        print("planner Selected:", action)
        if action == "FINISH":
            # Goal reached: produce the user-facing answer and stop.
            answer = format_answer(state)
            finish(state, answer)
            break

    # we execute the action
        observation = await execute_action(
            action,
            state,
            client
        )
    # we add that action in state
        add_action(
            state,
            action
        )
    # we remember whar happened
        record_observation(
            state,
            action,
            observation
        )
    # we move to the next iteration
        next_step(state)

    return state
