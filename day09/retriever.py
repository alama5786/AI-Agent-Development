from pathlib import Path

def load_document(file_path):
    """
    Load the content of a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the text file.
    """
    documents = {}
    folder = Path("knowledge")

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
    """
    # Placeholder implementation - replace with actual retrieval logic
    documents = load_document("knowledge")
    question = question.lower()

    for filename, content in documents.items():
        if question in content.lower():
            return filename, content
    return None, None