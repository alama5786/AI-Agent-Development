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

# store the conversation history
messages = []

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

    # save the AI response to the conversation history
    messages.append({"role": "assistant", "content": ai_response})
    
    # display the response
    print("\nAI: " + response.choices[0].message.content)
