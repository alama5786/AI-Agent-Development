"""
memory.py  --  long-term semantic memory for the agent (stage 11).

How it works:
    * Memories are rows in a local SQLite file (memory.db).
    * Each row stores the text AND its embedding (a vector of numbers capturing
      meaning) as JSON.
    * To recall, we embed the new query and rank stored memories by cosine
      similarity, so "What is my name?" finds "my name is Aziz" even without
      sharing exact words.
"""
import json
import sqlite3
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI

# SQLite file created in the current working directory.
DATABASE = "memory.db"

load_dotenv()

# Client used for the embeddings endpoint (must serve "nomic-embed-text").
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key= os.getenv("API_KEY")
)

def create_database():
    """Create the `memories` table if it does not exist yet (safe to call every run).

    Columns: id, user_message, assistant_message, embedding (JSON text),
    created_at (auto timestamp).
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            assistant_message TEXT,
            embedding TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()

def create_embedding (text):
    """Convert `text` to an embedding vector (list of floats) using nomic-embed-text."""
    response = client.embeddings.create(
        model = "nomic-embed-text",
        input = text
    )
    return response.data[0].embedding

def cosine_similarity (vector1, vector2):
    """Similarity between two vectors: 1 = same meaning direction, 0 = unrelated.

    Formula: (v1 . v2) / (|v1| * |v2|)
    """
    v1 = np.array (vector1)
    v2 = np.array (vector2)

    return np.dot(v1,v2)/(
        np.linalg.norm(v1)*
        np.linalg.norm(v2)
    )

def save_memory (user_message, assistant_message):
    """Store one conversation exchange (episodic memory).

    The user and assistant text are joined and embedded together, so a later
    search can match on either side of the conversation.
    """
    text = user_message + "\n" + assistant_message
    embedding = create_embedding(text)
    print(len(embedding))  # debug: embedding dimension

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # "?" placeholders are parameterised SQL: safe against SQL injection.
    cursor.execute(
        """
        INSERT INTO memories (
            user_message,
            assistant_message,
            embedding
        )
        VALUES ( ?,?,?)
        """,
        (
            user_message,
            assistant_message,
            json.dumps(embedding)   # list -> JSON text so SQLite can store it
        )
    )

    connection.commit()
    connection.close()


def search_semantic_memories(
        query,
        top_k=3,
        threshold = 0.50
):
    """Find the stored memories most similar in meaning to `query`.

    Args:
        query:     text to look up (e.g. the user's new request).
        top_k:     maximum number of memories to return.
        threshold: minimum cosine similarity to count as relevant.
    Returns:
        list of dicts (user_message, assistant_message, created_at, score),
        best match first.
    """
    # Embed the query once; compare it against every stored memory.
    query_embedding = create_embedding(query)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_message,
            assistant_message,
            embedding,
            created_at
        FROM memories
    """
    )

    rows = cursor.fetchall()
    connection.close()

    results = []
    for (
        user_message,
        assistant_message,
        embedding_json,
        created_at
    ) in rows:
        # JSON text -> list of floats
        memory_embedding = json.loads(embedding_json)

        score = cosine_similarity(
            query_embedding,
            memory_embedding
        )

        # Keep only memories that are similar enough.
        if score >= threshold:
            results.append({
                "user_message": user_message,
                "assistant_message": assistant_message,
                "created_at": created_at,
                "score": float(score)
            })

    # Highest score first.
    results.sort(
        key = lambda item: item["score"],
        reverse = True
    )

    print(results)  # debug output
    return results[:top_k]

def save_semantic_memory(fact):
    """Store a single extracted fact about the user (semantic memory).

    Unlike save_memory(), there is no conversation: the fact goes in the
    user_message column and assistant_message is left empty.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    embedding=create_embedding(fact)
    cursor.execute (
        """
        INSERT INTO memories 
        (
            user_message,
            assistant_message,
            embedding
        )
        VALUES (?,?,?)
        """,
        (
            fact, "", json.dump(embedding)
        )
    )
    connection.commit()
    connection.close()
