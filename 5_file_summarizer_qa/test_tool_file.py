# Manual test for tools.read_text_file: reads notes.txt via an absolute path
# and prints it. Change the path if the project lives elsewhere on your machine.
from tools import read_text_file

text = read_text_file("/Users/azizalam/AI/AI-Agent-Development/5_file_summarizer_qa/data/notes.txt")
print("Content of notes.txt:\n", text)
