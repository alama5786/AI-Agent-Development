"""
assistant.py  --  Stage 2: a role-based assistant using a system prompt.

Purpose:
    Show how a "system" message shapes the model's personality and behaviour.
    The user picks a persona (teacher / Python expert / travel guide) at start-up,
    and that persona is injected as the first message of the conversation.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# load the configuration from the .env file
load_dotenv()

# create AI client
client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
) 

print ("="*50)
print ("  My AI Assistant")
print ("="*50)

# Menu choice -> system prompt. Each prompt tells the model WHO to be and HOW to answer.
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

# store the conversation history.
# The first entry is the "system" message: it sets the persona for the whole chat.
# roles.get(...) falls back to a generic helper prompt if the choice is not 1/2/3.
messages = [
    {
     "role": "system", 
     "content": roles.get(user_role, "You are a helpful assistant that explains things in a way that a 12 year old can understand.")
    }
]

# Main chat loop: runs until the user types "exit" or "quit".
while True:

    user_input = input("\nYou: ")
    
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

    # Debug aid: print the whole history so you can SEE what the model receives each turn.
    print("\n---------Conversation History---------")
    for msg in messages:
        print(f"{msg['role'].capitalize()}: {msg['content']}")
