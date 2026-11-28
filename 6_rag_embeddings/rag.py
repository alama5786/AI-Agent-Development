"""
rag.py  --  Stage 6: Retrieval-Augmented Generation (RAG) chat assistant.

Purpose:
    Answer questions using OUR documents rather than only the model's training data.
    Pipeline:
        1. At start-up, embed every file in knowledge/ (done once).
        2. For each question, embed it and find the most similar document
           (cosine similarity).
        3. Paste that document into the prompt and let the LLM answer from it.
    The chat model comes from .env; embeddings come from local Ollama.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

from test_embedding import create_embedding
from retriever import load_document
from similarity import cosine_similarity 

# Step 1a: read all knowledge files -> {filename: text}
documents = load_document("knowledge")

# Step 1b: pre-compute one embedding per document so we don't re-embed every question.
document_embeddings = {}
for filename, content in documents.items():
    document_embeddings[filename] = create_embedding(content)

# load the configuration from the .env file
load_dotenv()

# create AI client (for the chat model)
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

    # Step 2: embed the question and pick the single best-matching document.
    question_embedding = create_embedding(user_input)

    best_score = -1
    best_document = None
    for filename, embedding in document_embeddings.items():
        score = cosine_similarity(question_embedding, embedding)
        if score > best_score:
            best_score = score
            best_document = filename

    content = documents[best_document]

    # Step 3: "augment" the prompt with the retrieved text and constrain the answer to it.
    prompt = f"""Answer the question using only the following information.
    content: {content}
    Question: {user_input}"""
    
    # save the user input (the augmented prompt) to the conversation history
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
