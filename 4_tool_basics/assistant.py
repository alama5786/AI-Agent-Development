"""
assistant.py  --  Stage 4: role-based chat assistant + simple keyword tools.

Purpose:
    Extend the role-based chat with tool use. Before a message is sent to the LLM,
    we check whether it matches a local tool (time / dice / password). If it does,
    the tool answers directly; otherwise the LLM handles the message.
"""
from openai import OpenAI
from dotenv import load_dotenv
from tool_manager import execute_tool
import os

# NOTE: these direct imports are not used here (tool_manager calls them for us).
from tools import (
    get_current_time, roll_dice, generate_password
)
# load the configuration from the .env file
load_dotenv()

# create AI client
client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
) 

print ("="*50)
print ("  My AI Assistant")
print ("="*50)

# Menu choice -> system prompt (the persona the model will adopt).
roles ={
    "1": "you are a friendly schjool teacher, explain every concept in a simple way with real-world examples that a 12 year old can understand.",
    "2": "you are a python expert, explain every concept in a simple way with real-world examples that a 12 year old can understand.",
    "3": "you are an experienced travel guide, recommend best food, travel tips and transporation options"
}

print ("\nSelect a role for the AI Assistant:")

print ("1. Friendly School Teacher")
print ("2. Python Expert")
print ("3. Travel Guide")

# get the user's choice of role
user_role = input("\nEnter the number corresponding to your desired role: ")

# store the conversation history; the first message is the persona (system prompt)
messages = [
    {
     "role": "system", 
     "content": roles.get(user_role, "You are a helpful assistant that explains things in a way that a 12 year old can understand.")
    }
]

while True:

    user_input = input("\nYou: ")

    # Step 1: try the local tools first. If one matched, show its result and
    # skip the LLM entirely for this turn.
    tool_result = execute_tool(user_input)
    if tool_result:
        print("\n AI: " + tool_result)
        continue
    
    # Step 2: exit command.
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the AI Assistant. Goodbye!")
    break

    # save the user input to the conversation history
    messages.append({"role": "user", "content": user_input})

    # send the conversation history to the AI model and get a response
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    ai_response = response.choices[0].message.content

     # display the response
    print("\nAI: " + response.choices[0].message.content)

    # save the AI response to the conversation history
    messages.append({"role": "assistant", "content": ai_response})

    # Debug aid: show the full history sent to the model each turn.
    print("\n---------Conversation History---------")
    for msg in messages:
        print(f"{msg['role'].capitalize()}: {msg['content']}")
