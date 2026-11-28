# Manual test for task_planner.decompose_task: a two-part request should come
# back as two separate tasks. Needs a live LLM configured in .env.
from task_planner import decompose_task

user_request = ( 
    "generate password and tell me the current time"
    )

tasks = decompose_task(user_request)

print ("\nTask Plan")
print ("------------")

for task in tasks:
    print("-", task)
