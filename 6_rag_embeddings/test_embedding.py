"""
test_embedding.py  --  embedding helper + a demo of semantic similarity.

Significance:
    Defines create_embedding(), which rag.py imports to turn text into a vector
    using a LOCAL Ollama server and the "nomic-embed-text" model. Running the file
    directly also demonstrates that two sentences with similar meaning get a high
    cosine similarity score.
    Caution: the demo code below runs at import time too, so importing this module
    triggers the extra embedding call and the prints.
"""
from openai import OpenAI
from similarity import cosine_similarity

sentence1 = "Python is a programming language"
sentence2 = "Python is a widely used software language"

# Ollama exposes an OpenAI-compatible API locally; the api_key is a dummy value.
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def create_embedding(content):
    """Return the embedding vector (list of floats) for one piece of text."""
    embedding1 = client.embeddings.create(
        model="nomic-embed-text",
        input=[content]
    ).data[0].embedding
    return embedding1

# Demo: embed two sentences in a single request (a batch).
response = client.embeddings.create(
    model="nomic-embed-text",
    input=[sentence1, sentence2]
)

# Sort by .index so vectors line up with the order of the inputs.
embeddings = sorted(response.data, key=lambda item: item.index)
embedding1 = embeddings[0].embedding
embedding2 = embeddings[1].embedding
# Higher score = more similar meaning.
score = cosine_similarity(embedding1, embedding2)

print(f"Cosine similarity score between the two sentences: {score}")
embedding = embedding1
print("Embedding type:", type(embedding))
print("Embedding length:", len(embedding))
