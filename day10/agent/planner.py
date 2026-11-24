from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key= os.getenv("API_KEY")
)

def build_tool_descriptions(tools):
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
    tool_descriptions = build_tool_descriptions(tools)
    prompt = f"""
    You are an AI planner
    Your job is to select the next task and the best tool to complete it.
    User request:
    {state["user_request"]}
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

