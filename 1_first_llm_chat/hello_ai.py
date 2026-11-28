"""
hello_ai.py  --  Stage 1: the simplest possible LLM call.

Purpose:
    Prove that our environment works end to end: read credentials from .env,
    connect to an OpenAI-compatible endpoint, send ONE prompt and print the reply.
    Everything later in this project (chat loops, tools, RAG, agents, memory)
    builds on this single request/response round trip.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load API_KEY, BASE_URL and MODEL from the local .env file into environment variables.
# Keeping secrets in .env means they never get hard-coded or committed in source.
load_dotenv()

# The OpenAI client works with any OpenAI-compatible server (OpenAI, Ollama, etc.)
# because we make the server address configurable through BASE_URL.
client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
) 

# Send a single, stateless chat request. "messages" is the conversation so far;
# here it only holds one user message, so the model has no prior context.
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {
        "role": "user", 
         "content": "explain python to 12 year old"
         }
         ]
)

# The reply text lives in the first "choice" of the response object.
print(response.choices[0].message.content)
