# Manual test of the memory database: create the table, store three memories,
# then semantically search for "What is my name" and print the ranked matches.
# Needs the embedding model (nomic-embed-text) to be reachable.
from memory import *

create_database()

save_memory(
    "my name is Aziz Alam",
    "nice to see you Aziz",

)

save_memory (
    "I am learning AI Agent Development",
    "AI is userful skill to learn"
)

save_memory(
    "I am learing about MCP",
    "MCP allows AI applications to use tools"
)

results = search_semantic_memories (
    "What is my name"
)

print ("\nRelevant Memories")
print ("-------------------")

for result in results:
    print("\nScore:", result["score"])
    print("user:", result["user_message"])
    print("Assistant:", result["assistant_message"])
