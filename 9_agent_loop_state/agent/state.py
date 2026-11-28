"""
state.py  --  the agent's working memory for ONE request (stage 9).

Significance:
    The state is a plain dict that travels through the agent loop. The planner reads
    it to decide the next step; the loop writes to it after each action. Keeping all
    progress in one place is what lets an agent do multi-step work.
"""

def create_state (user_request, max_steps = 5):
    """Build a fresh state for a new user request.

    max_steps is a safety limit so a confused planner cannot loop forever.
    """
    return {
        "user_request": user_request,   # what the user asked
        "current_step":0,               # iteration counter
        "max_steps":max_steps,          # hard stop for the loop
        "actions":[],                   # tools already executed (in order)
        "observations":[],              # what each tool returned
        "finished":False,               # True once the agent is done
        "final_answer":""               # text shown to the user
    }

def add_action(state, action):
    """Remember that `action` (a tool name) has been executed."""
    state["actions"].append(action)

def record_observation(state, action, observation):
    """Store a tool's output together with the step and tool that produced it."""
    state["observations"].append(
        {
            "step": state["current_step"],
            "action": action,
            "observation": observation
        }
    )

def next_step(state):
    """Advance the iteration counter by one."""
    state["current_step"]+=1

def can_continue(state):
    """True while the agent is not finished and has steps left."""
    return (
        not state["finished"]
        and state["current_step"]<state["max_steps"]
    )

def finish(state, answer):
    """Mark the run complete and save the final answer."""
    state["final_answer"]=answer
    state["finished"] = True
