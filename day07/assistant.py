from openai import OpenAI
from dotenv import load_dotenv
import os

from planner import choose_tool

from tools import get_current_time, roll_dice, generate_password

# load the configuration from the .env file
load_dotenv()

# create an OpenAI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))

print ("="*50)
print ("  My AI Assistant")
print ("="*50)  

while True:
    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the AI Assistant. Goodbye!")
        break
    tool = choose_tool(user_input)
    if tool == "get_current_time":
        result = get_current_time()
    elif tool == "roll_dice":
        result = roll_dice()
    elif tool == "generate_password":
        length = 12  # default length
        result = generate_password(length)
    else:
        result = "I'm sorry, I cannot assist with that request."    

    prompt = f"""You are an AI assistant.
User request: {user_input}
Tool chosen: {tool}
Tool result: {result}
Please provide a response to the user based on the tool result and the user request.
"""
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}
                 ]
    )
    print("\nAI: " + response.choices[0].message.content.strip())