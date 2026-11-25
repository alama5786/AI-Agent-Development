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
    Your job is to decide only the next action.
    User request:
    {state["user_request"]}
    Completed Actions:
    {state["actions"]}
    Previous Observations:
    {state["observations"]}
    Available tools:
    {tool_descriptions}
    Rules:
    1. Choose only one next action
    2. Never repeat an action that has already been completed
    3. Use the observations to decide what is still required
    4. if the user's request has been completely satisfied, return FINISH
    5. Return only the tool name or FINISH
    6. Do not explain your answer

    Next Action:
    """
    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI planner"
            },
            {
                "role": "User",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()

