"""
assistant.py  --  Stage 1: an interactive chat assistant with conversation memory.

Purpose:
    Turn the one-shot call from hello_ai.py into a back-and-forth chat.
    The key idea: LLMs are STATELESS. They only "remember" what we send them,
    so we keep a growing `messages` list and re-send the whole thing every turn.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

# load the configuration from the .env file
load_dotenv()

# create AI client (OpenAI-compatible; the server is chosen by BASE_URL)
client = OpenAI(api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL")
) 

print ("="*50)
print ("  My AI Assistant")
print ("="*50)

# Conversation history. Each entry is {"role": "user"|"assistant", "content": text}.
# Sending this full list each turn is what gives the model short-term memory.
messages = []

# Main chat loop: runs until the user types "exit" or "quit".
while True:

    user_input = input("\nYou: ")
    
    # Exit command: leave the loop and end the program.
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

    # save the AI response to the conversation history so the next turn can see it
    messages.append({"role": "assistant", "content": ai_response})
    
    # display the response
    print("\nAI: " + response.choices[0].message.content)
