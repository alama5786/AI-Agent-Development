"""
memory_extractor.py  --  decides what is worth remembering long term.

Significance:
    Saving every message would bury useful facts in noise. This module asks the LLM
    to read one exchange and return ONLY a durable fact about the user (preference,
    goal, skill, project...) or "NONE". The result feeds save_semantic_memory().
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# load the configuration from the .env file
load_dotenv()

# create an OpenAI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

def extract_memory (
        user_message,
        assistant_message
):
    """Return the fact to remember from this exchange, or "NONE".

    Args:
        user_message:      what the user said.
        assistant_message: how the assistant replied.
    """
    # The prompt lists what IS and IS NOT worth storing so temporary requests
    # (time, calculations, tool output) don't pollute long-term memory.
    prompt = f"""
    You are a memory extraction system.
    Read the conversation below and determine whether it contain useful lon-term
    information about the user.

    User:
    {user_message}

    Assiatnt:
    {assistant_message}

    store information only if it will be useful in future conversations.
    Userful information includes:
    -preferences
    -interests
    -goals
    -skills
    -projects
    -important user facts

   Do NOT Store:
    -temporary questions
    -current time
    -random calculations
    -one time requests
    -tool results
    -casual conversations

   if useful information exists, returns only the fact that should be 
   remembered:

   NONE
"""
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content":(
                    "You extract useful long-term memories"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
