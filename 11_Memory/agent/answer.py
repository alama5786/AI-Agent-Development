"""
answer.py  --  writes the final user-facing reply (stage 11).

New in this stage: the prompt also contains the retrieved long-term memories, so
answers such as "what is my name?" can use facts saved in earlier conversations.
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
    Relevant Previous Memories:
    {state["memories"]}
    Tasks:
    {state["tasks"]}
    Actions:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Intermediate Results:
    {state["results"]}
    Use relevant previous memories when they help answer the user's questions
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
