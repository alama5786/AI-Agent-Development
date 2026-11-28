"""
task_planner.py  --  breaks a user request into smaller tasks (stage 11).

New in this stage: "Critical Rules" tell the model to return NO tasks for greetings,
personal introductions, memory questions and general knowledge. Those requests need
no tools, so the planner can go straight to FINISH and answer from memory/knowledge.
"""
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def decompose_task (user_request):
    """Ask the LLM to split `user_request` into short tasks.

    Returns:
        list[str]: one task per non-empty line of the reply (may be ["NONE"]
        when the request needs no tools).
    """
    prompt = f"""
    You are an AI task planner
    Break user request into smaller tasks
    Rules:
    1. Create only necessary tasks
    2. Put tasks in execution order
    3. Each task should be a short action
    4. Return one task per line
    5. Do not number the tasks
    6. Do not explain anyhting
    Critical Rules:
    Return NO tasks ( or "NONE") if user request belong to any of the following categories:
    1. Greetings or casual conversation (e.g. "hi", "hello, how are you")
    2. Intruductions or personal details (e.g. "my name is Aziz Alam", "I live in London")
    3. Memory questions about the past interactions(e.g. "what is my name?", "what did we discuss earlier")
    4. Genral knowledge / Q&A questions that can be answered directly without tools(e.g. "what is machine 
    learning?"," "explain gravity")
    User Request:
    {user_request}
    """

    response = client.chat.completions.create(
        model = os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You are an AI task planner"
            },
            {
                "role": "user",
                "content":prompt
            }
        ]
    )

    # Parse the reply: each non-blank line becomes one task.
    result = response.choices[0].message.content.strip()
    tasks = []
    for task in result.splitlines():
        line = task.strip()
        if line:
            tasks.append(line)
    return tasks
