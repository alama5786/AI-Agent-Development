from openai import OpenAI
from dotenv import load_dotenv
import os

from test_embedding import create_embedding
from retriever import load_document
from similarity import cosine_similarity 

documents = load_document("knowledge")

document_embeddings = {}
for filename, content in documents.items():
    document_embeddings[filename] = create_embedding(content)

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

    question_embedding = create_embedding(user_input)

    best_score = -1
    best_document = None
    for filename, embedding in document_embeddings.items():
        score = cosine_similarity(question_embedding, embedding)
        if score > best_score:
            best_score = score
            best_document = filename

    content = documents[best_document]

    prompt = f"""Answer the question using only the following information.
    content: {content}
    Question: {user_input}"""
    
    # save the user input to the conversation history
    messages.append({"role": "user", "content": prompt})

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
