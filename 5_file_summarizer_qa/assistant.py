"""
assistant.py  --  Stage 5: file summarizer and document Q&A.

Purpose:
    Add two file-based commands on top of the keyword tools and role-based chat:
        summarize <file>            -> ask the LLM to summarise data/<file>
        ask <file> <question>       -> answer a question using ONLY that file's text
    This is the basic "give the model a document in the prompt" pattern that
    RAG (stage 6) later improves by retrieving only the relevant parts.
"""
from openai import OpenAI
from dotenv import load_dotenv
from tool_manager import execute_tool
import os


from tools import (
    get_current_time, roll_dice, generate_password, read_text_file
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

    # ---- Command 1: "summarize <filename>" ----
    text = user_input.lower()
    if text.startswith("summarize "):
        # Everything after the command word is the file name inside data/.
        filename = user_input[len("summarize "):].strip()
        file_content = read_text_file("data/" + filename)

        # Put the whole document into the prompt and ask for a summary.
        prompt = f"Summarize the following document:\n\n{file_content}"

        response = client.chat.completions.create(model=os.getenv("MODEL"), messages=[{"role": "user", "content": prompt}])
        ai_response = response.choices[0].message.content
        print("\nAI: " + ai_response)
        continue

    # ---- Command 2: "ask <filename> <question>" ----
    if text.startswith("ask "):
        # maxsplit=2 -> ["ask", filename, "rest of the sentence is the question"]
        parts=user_input.split(maxsplit=2)
        print(parts)  # debug output
        filename = parts[1].strip()
        question = parts[2].strip()

        file_content = read_text_file("data/" + filename)

        # Grounding prompt: instructs the model to answer only from the document,
        # which reduces hallucination.
        prompt = f""" 
                  you are given a document and a question, your task is to answer the question 
                  based on the content of the document. if the answer is not present 
                  in the document, please respond 
                  with "The answer is not present in the document.
                  
                  document: {file_content}
                  question: {question}
                  """                  
        response = client.chat.completions.create(model=os.getenv("MODEL"), messages=[{"role": "user", "content": prompt}])
        ai_response = response.choices[0].message.content
        print("\nAI: " + ai_response)
        continue

    # ---- Local keyword tools (time / dice / password) ----
    tool_result = execute_tool(user_input)
    if tool_result:
        print("\n AI: " + tool_result)
        continue
    
    # ---- Exit command ----
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the AI Assistant. Goodbye!")
    break

    # ---- Normal chat with the LLM (keeps history) ----
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
