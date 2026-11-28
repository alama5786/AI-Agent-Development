"""
loop.py  --  the agent loop with task planning AND long-term memory (stage 11).

Flow:
    1. create state
    2. RECALL: search the memory database for memories relevant to the request
    3. decompose the request into tasks
    4. repeat: planner picks (TASK, TOOL) -> execute -> record -> mark task done
    5. on FINISH: write the answer, SAVE the conversation, and extract/save any
       durable fact about the user
"""
from state import *
from task_planner import decompose_task
from memory import search_semantic_memories
from memory import save_memory
from memory import save_semantic_memory
from memory_extractor import extract_memory

def parse_decision (decision):
    """Extract (task, tool) from the planner's reply.

    Expected lines:  "TASK: <task>"  and  "TOOL: <tool>".
    A missing part stays None so the caller can treat the decision as invalid.
    """
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
    """Run the agent on `user_request` and return the final state."""
    # create the agent state
    state = create_state (user_request)

    # Add following code to retrieve memories
    # RECALL: fetch the 3 most similar past memories and give them to the agent.
    memories =  search_semantic_memories (
        user_request,
        top_k=3
    )
    for memory in memories:
        add_memory(state, memory)

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
            # SAVE: store this exchange (request + answer) as an episodic memory.
            save_memory(
                user_request,
                format_answer(state)
            )

            # EXTRACT: ask the LLM whether the exchange contains a lasting fact
            # about the user; "NONE" means nothing worth remembering.
            fact = extract_memory(
                user_request,
                format_answer
            )

            if fact != "NONE":
                save_semantic_memory(fact)

            break

        # Extract task and tool
        task, tool = parse_decision(decision)

        # Malformed planner output: log it, burn a step and try again.
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

        # Mark selected task complete only if the tool did not report an error;
        # otherwise leave it pending and tell the planner to rethink.
        if not str(observation).lower().startswith("error"):
            complete_task(state, task)
        else:
            add_result(state, "The previous action failed. The planner must reconsider")

        next_step(state)

    # step limit reached without FINISH
    if not state["finished"]:
        finish(state, format_answer(state))

    return state
