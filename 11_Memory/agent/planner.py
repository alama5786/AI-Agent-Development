"""
planner.py  --  picks the next task AND the tool for it (stage 11).

New in this stage: the prompt includes retrieved long-term memories, and extra rules
(9-12) let the planner return FINISH immediately when no tool is needed (for example
greetings or "what is my name?"), and forbid inventing tool names.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key= os.getenv("API_KEY")
)

def build_tool_descriptions(tools):
    """Format MCP tool objects (name + docstring) as text for the planner prompt."""
    descriptions = ""

    for tool in tools:
        descriptions +=f"""
    Tool:
    {tool.name}
    Description:
    {tool.description}
    ------------------
    """
    return descriptions

def planner (state, tools):
    """Ask the LLM for the next decision.

    Returns:
        "TASK: <task>\\nTOOL: <tool>"  or  "FINISH".
    """
    tool_descriptions = build_tool_descriptions(tools)
    # The prompt exposes the whole state (including memories) so the model can
    # see progress, past knowledge about the user and any failures.
    prompt = f"""
    You are an AI planner
    Your job is to select the next task and the best tool to complete it.
    User request:
    {state["user_request"]}
     Relevant Previous Memories:
    {state["memories"]}
    Tasks:
    {state["tasks"]}
    Completed Actions:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Intermediate Results:
    {state["results"]}
    Available tools:
    {tool_descriptions}
    Rules:
    1. Select only ONE pending task
    2. Select the best available tool for that task
    3. do not select the completed task
    4. Use the observations and results
    5. If an action fail, reconsider the plan
    6. If all tasks are completed, return FINISH
    7. Return exactly:
    TASK: <task>
    TOOL: <tool>
    8. Do not explain anything.
    9. User previous observations and relevant memories.
    10. If the request can be answered directly using conventional memory,
        standard knowledge, or if tasks list is empty/NONE, respond ONLY with:FINISH
    11. If a tool is required to complete a pending task, respond strictly in this format:
        TASK: <task description>
        TOOL: <extract tool name from available tools>
    12. Never output "TOOL: none" or invent tool names. If no valid tool from 
        available tools is needed, retun FINISH
    Next Descision:
    """
    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI planner"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
