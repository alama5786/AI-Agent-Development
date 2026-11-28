"""
planner.py  --  Stage 7: lets the LLM choose which tool to use.

Significance:
    Replaces hard-coded keyword matching (stage 4) with an LLM "planner".
    We describe the available tools in a prompt and the model answers with the
    tool name that best fits the request. This is the core idea behind agents:
    the model decides the action, our code carries it out.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
)

def choose_tool(user_request):
   """Ask the LLM which tool fits `user_request`.

   Returns:
       One of "get_current_time", "roll_dice", "generate_password" or "none"
       (lower-cased, whitespace stripped) -- exactly what the model replied.
   """
   # The prompt lists every tool and forces a one-word answer so the output
   # is easy to compare against in assistant.py.
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
   # Normalise the reply so "Roll_Dice \n" still matches "roll_dice".
   tool_choice = response.choices[0].message.content.strip().lower()
   return tool_choice   
