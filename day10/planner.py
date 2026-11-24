from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

def choose_tool(user_request):
   planner_prompt = f"""
You are an AI assistant.

Available tools:
1. get_current_time: Returns the current time.
2. roll_dice: Rolls a dice and returns the result.
3. generate_password: Generates a random password of specified length.

if no tool is suitable for the user's request, respond with 'none'.

Your task is to choose the most appropriate tool based on the user's request.
User request: {user_request}
Please respond with the tool name only (e.g., get_current_time, roll_dice, generate_password) or 'none' if no tool is suitable.
"""
   response = client.chat.completions.create(
       model=os.getenv("MODEL"),
       messages=[{"role": "SYSTEM", "content": "your are an AI planner"},
                    {"role": "user", "content": planner_prompt}
                 ]
   )
   tool_choice = response.choices[0].message.content.strip().lower()
   return tool_choice   