from state import *
from task_planner import decompose_task


def parse_decision (decision):
    task = None
    tool = None
    for line in decision.splitlines():
        line = line.strip()

        if line.startswith("TASK:"):
            task = line[5:].strip()
        elif line.startswith("TOOL:"):
            tool = line[5:].strip()
    return task,tool

async def run_agent_loop (
    user_request,
    planner,
    execute_action,
    format_answer,
    tools,
    client
):
    # create the agent state
    state = create_state (user_request)

    # break the user's request into tasks
    planned_tasks = decompose_task (user_request )

    # store the tasks into state
    for task in planned_tasks:
        add_task(state, task)

    print ("\nTask Plan")
    print ("------")
    for item in state["tasks"]:
        print ("-", item["task"])

    while can_continue(state):

        print (f"\n---step {state['current_step'] + 1 }---")

        # ask the planner for the next decision
        decision = planner (state, tools)
        print ("Planner Decision:", decision)

        # check whether the goal is complete
        if decision.strip()=="FINISH":
            finish(state, format_answer(state))
            break

        # Extract task and tool
        task, tool = parse_decision(decision)

        if not task or not tool:
            add_result(state, "Invalid Planner decision")
            next_step(state)
            continue

        state["current_task"] = task

        # Execute the selected tool
        observation = await execute_action(tool, state, client)
        print ("observations:", observation)

        # Update state
        add_action(state, tool)
        record_observation(state, tool, observation)
        add_result(state, observation)

        # Mark selected task complete
        if not str(observation).lower().startswith("error"):
            complete_task(state, task)
        else:
            add_result(state, "The previous action failed. The planner must reconsider")

        next_step(state)

    # step limit reached without FINISH
    if not state["finished"]:
        finish(state, format_answer(state))

    return state
