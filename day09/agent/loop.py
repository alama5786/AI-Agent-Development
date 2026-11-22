from state import *

async def run_agent_loop (
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):
    state = create_state (user_request)

    #while can_continue: "This is the heart of our agent"

    while can_continue(state):

    # The planner decide what to do next
        action = planner(state, tools)
        print("planner Selected:", action)
        if action == "FINISH":
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
