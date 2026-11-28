"""
state.py  --  the agent's working memory for ONE request (stage 11).

New in this stage: a `memories` list holding relevant long-term memories retrieved
from the database, so the planner and answer writer can use past conversations.
"""
def create_state (user_request, max_steps = 5):
    """Build a fresh state. max_steps is the safety limit for the loop."""
    return {
        "user_request": user_request,   # what the user asked
        "tasks":[],                     # [{"task": str, "status": "pending"|"completed"}]
        "current_task":None,            # task being worked on right now
        "current_step":0,               # iteration counter
        "max_steps":max_steps,          # hard stop for the loop
        "actions":[],                   # tools already executed
        "observations":[],              # detailed tool outputs (step, action, output)
        "results":[],                   # simple list of outputs / notes for the planner
        "memories":[],                  # relevant long-term memories (from memory.py)
        "finished":False,
        "final_answer":""
    }

def add_memory(state, memory):
    """Attach one retrieved memory (a dict from search_semantic_memories) to the state."""
    state["memories"].append(memory)

def add_task(state, task):
    """Append a new task in the "pending" status."""
    state["tasks"].append({
        "task": task,
        "status":"pending"
    })

def complete_task(state, task):
    """Mark the first task whose text equals `task` as completed."""
    for item in state["tasks"]:
        if item["task"] == task:
            item["status"]="completed"
            return
        
def add_result(state, result):
    """Store an intermediate result (tool output or a note such as an error hint)."""
    state["results"].append(result)

def add_action(state, action):
    """Remember that tool `action` has been executed."""
    state["actions"].append(action)

def get_pending_tasks(state):
    """Return the text of every task that is still pending."""
    return[
        item["task"]
        for item in state["tasks"]
            if item["status"] == "pending"
    ]

def all_tasks_completed (state):
    """True when no task is left pending."""
    return all (
        item["status"]=="completed"
        for item in state["tasks"]  
    )

def record_observation(state, action, observation):
    """Store a tool's output with the step and tool that produced it."""
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
