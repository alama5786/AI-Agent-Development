# Manual test for memory_extractor.extract_memory: this exchange contains a durable
# user goal, so the model should return a fact (not "NONE"). Needs a live LLM.
from memory_extractor import extract_memory

memory = extract_memory(
    "I am Aziz. I am learning AI agent engineering. It is my 2027 year goal",
    "Hi Aziz, thats a useful thing to learn. Do you need my help?"
)

print("Extracted Memory")
print(memory)
