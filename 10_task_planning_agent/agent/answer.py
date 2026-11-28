"""
answer.py  --  writes the final user-facing reply (stage 10).

Significance:
    Moved out of runner.py into its own module. It gives the LLM everything the
    agent collected (tasks, actions, observations, results) and asks for a short
    natural answer that hides internal details.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# load the configuration from the .env file
load_dotenv()

# create an OpenAI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

def format_answer(state):
    """Return a natural, concise answer built from the final `state`."""
    prompt = f"""
    The user asked:
    {state["user_request"]}
    Tasks:
    {state["tasks"]}
    Actions:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Intermediate Results:
    {state["results"]}
    Give the user a natural and concise answer:
    Do not mention:
    - planner
    - agent loop
    - mcp
    - Internal state
    - tools
    - Internal reasoning
    """

    response = client.chat.completions.create(model = os.getenv("MODEL"),
                                              messages=[
                                                  {
                                                  "role":"user",
                                                  "content":prompt
                                                  }
                                              ]
                                              )
    return response.choices[0].message.content.strip()
