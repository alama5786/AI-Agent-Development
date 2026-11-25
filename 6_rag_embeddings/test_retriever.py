from retriever import load_document
from retriever import retrieve

filename, content = retrieve ("weather")
print(f"Retrieved from {filename}: {content}")
