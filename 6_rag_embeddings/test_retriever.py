# Manual test for the keyword retriever: looks for "weather" inside the
# knowledge/*.txt files and prints which file matched and its content.
from retriever import load_document
from retriever import retrieve

filename, content = retrieve ("weather")
print(f"Retrieved from {filename}: {content}")
