"""
assistant.py  --  Stage 7: assistant where the LLM plans and then explains.

Flow for every user message:
    1. PLAN    - planner.choose_tool() asks the LLM which tool to use.
    2. ACT     - our code runs that tool (time / dice / password).
    3. RESPOND - a second LLM call turns the raw tool result into a friendly reply.
"""
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

    # Step 1 (plan): let the LLM pick a tool name.
    tool = choose_tool(user_input)

    # Step 2 (act): run the chosen tool; unknown/"none" falls through to an apology.
    if tool == "get_current_time":
        result = get_current_time()
    elif tool == "roll_dice":
        result = roll_dice()
    elif tool == "generate_password":
        length = 12  # default length
        result = generate_password(length)
    else:
        result = "I'm sorry, I cannot assist with that request."    

    # Step 3 (respond): give the model the request + tool result to phrase the answer.
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
