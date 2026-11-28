"""
task_planner.py  --  breaks a user request into smaller tasks (stage 10).

Significance:
    Planning at two levels makes the agent more reliable: FIRST decompose the whole
    request into an ordered to-do list (this file), THEN let planner.py pick the tool
    for one task at a time.
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
        list[str]: one task per non-empty line of the model's reply.
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
