from openai import OpenAI
from similarity import cosine_similarity

sentence1 = "Python is a programming language"
sentence2 = "Python is a widely used software language"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def create_embedding(content):
    embedding1 = client.embeddings.create(
        model="nomic-embed-text",
        input=[content]
    ).data[0].embedding
    return embedding1

response = client.embeddings.create(
    model="nomic-embed-text",
    input=[sentence1, sentence2]
)

embeddings = sorted(response.data, key=lambda item: item.index)
embedding1 = embeddings[0].embedding
embedding2 = embeddings[1].embedding
score = cosine_similarity(embedding1, embedding2)

print(f"Cosine similarity score between the two sentences: {score}")
embedding = embedding1
print("Embedding type:", type(embedding))
print("Embedding length:", len(embedding))
