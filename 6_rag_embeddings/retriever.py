"""
retriever.py  --  loads the knowledge base and offers a naive keyword lookup.

Significance:
    The "R" in RAG (Retrieval-Augmented Generation). load_document() reads every
    .txt file in knowledge/ so rag.py can embed them. retrieve() is the early,
    simple retrieval version (exact substring match) that embeddings later replace.
"""
from pathlib import Path

def load_document(file_path):
    """
    Load the content of a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the text file.

    Implementation note: despite the argument, the folder is hard-coded to
    "knowledge" and the function returns a dict {filename: file text}
    for all *.txt files in it.
    """
    documents = {}
    folder = Path("knowledge")

    # Read each text file in the knowledge folder, keyed by its file name.
    for file in folder.glob("*.txt"):
        documents[file.name] = file.read_text(encoding='utf-8')
    return documents


def retrieve (question):
    """
    Retrieve the answer to a question from the loaded documents.

    Args:
        question (str): The question to be answered.    

    Returns:
        str: The answer to the question.

    Implementation note: returns (filename, content) of the first document that
    contains the whole question as a substring, or (None, None). This is keyword
    matching only -- it does not understand meaning (see rag.py for that).
    """
    # Placeholder implementation - replace with actual retrieval logic
    documents = load_document("knowledge")
    question = question.lower()

    for filename, content in documents.items():
        if question in content.lower():
            return filename, content
    return None, None
