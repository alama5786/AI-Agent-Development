# Advanced AI Agent with Task Planning: Interview Guide

A complete walkthrough of the `day10/agent/` project: what each file does, how the pieces connect, and how to explain it in an interview.

---

## 1. The one-minute pitch (memorise this)

> "I built an AI agent in Python that takes a natural-language request, **decomposes** it into sub-tasks, then runs a **plan → act → observe** loop. In each step an LLM planner picks the next pending task and the best tool. The tool is executed on an **MCP server** (Model Context Protocol). The result is saved into a shared **state** object and fed back to the planner. When all tasks are done, the planner says `FINISH` and an LLM turns the collected observations into a natural answer. The LLM runs locally through Ollama, using an OpenAI-compatible API."

---

## 2. What is an "agent" (vs a plain chatbot)?

| Chatbot | Agent |
|---|---|
| One prompt, one answer | Loops: think, act, observe, think again |
| Only knows its training data | Can call **tools** (time, dice, APIs, DBs) |
| No memory of steps | Keeps **state** (tasks, actions, observations) |
| Can't plan | **Decomposes** goals into tasks |

**Core agent formula:** `LLM (brain) + Tools (hands) + State/Memory + Loop (control flow)`

---

## 3. Architecture at a glance

```
                    ┌────────────────────────────┐
   User request ──► │         runner.py          │  entry point
                    └─────────────┬──────────────┘
                                  │ 1. connect() to MCP server
                                  │ 2. discover_tool()
                                  ▼
                    ┌────────────────────────────┐
                    │          loop.py           │  run_agent_loop()
                    │  (the agent's heart)       │
                    └─────────────┬──────────────┘
      ┌───────────────────────────┼───────────────────────────────┐
      ▼                           ▼                               ▼
┌──────────────┐        ┌──────────────────┐             ┌──────────────┐
│task_planner  │        │   planner.py     │             │  executor.py │
│decompose_task│        │ picks TASK+TOOL  │             │execute_action│
│ (LLM call #1)│        │ (LLM call per    │             └──────┬───────┘
└──────┬───────┘        │  step)           │                    ▼
       │                └────────┬─────────┘             ┌──────────────┐
       ▼                         │                       │ mcp_client.py│
┌──────────────────────────────────────────┐             │ call_tool()  │
│                state.py                  │◄────────────┴──────┬───────┘
│ tasks, actions, observations, results,   │                    ▼
│ current_step, finished, final_answer     │             ┌──────────────┐
└──────────────────┬───────────────────────┘             │  server.py   │
                   │ when FINISH                         │ FastMCP tools│
                   ▼                                     └──────────────┘
            ┌──────────────┐
            │  answer.py   │  format_answer(): LLM writes the final reply
            └──────────────┘
```

---

## 4. Step-by-step flow (what happens when you run `python3 runner.py`)

Example request: **"generate password and tell me the current time"**

1. **`runner.py` starts.** It calls `connect()`, which launches `server.py` as a subprocess over stdio and returns an MCP client.
2. **Tool discovery.** `discover_tool(mcp)` asks the server what tools exist (`current_time`, `roll_dice`, `generate_password`).
3. **User input.** `input("User:")` reads the request.
4. **Task decomposition (LLM call #1).** `decompose_task()` returns something like:
   - `Generate a password`
   - `Get the current time`
5. **State creation.** `create_state()` makes the shared memory dict. Each task is added with status `pending`.
6. **The agent loop starts** (`while can_continue(state)`):
   - **Plan:** `planner(state, tools)` sends the request, tasks, past actions, observations, results and tool descriptions to the LLM. It replies `TASK: ...` / `TOOL: ...` or `FINISH`.
   - **Parse:** `parse_decision()` extracts the task name and tool name from that text.
   - **Act:** `execute_action()` calls the tool on the MCP server.
   - **Observe:** the tool output is saved with `add_action`, `record_observation` and `add_result`.
   - **Update:** if the output doesn't start with "error", `complete_task()` marks the task done. Otherwise a failure note is added so the planner reconsiders.
   - `next_step()` increments the step counter.
7. **Finish.** When the planner returns `FINISH` (or max steps is hit), `format_answer()` makes an LLM call that turns the raw observations into a friendly answer, and `finish()` stores it.
8. **Output and cleanup.** `runner.py` prints `state["final_answer"]` and calls `disconnect(mcp)`.

**Sequence of a 2-task run:**

```
Step 1: Planner → "TASK: Generate a password / TOOL: generate_password"
        Execute → "aB3$..."        → task 1 = completed
Step 2: Planner → "TASK: Get the current time / TOOL: current_time"
        Execute → "2026-11-24 ..."  → task 2 = completed
Step 3: Planner → "FINISH"
        format_answer() → "Here's your password ... and the time is ..."
```

---

## 5. File-by-file explanation

### 5.1 `server.py`: the tool provider (MCP server)

- Uses **FastMCP** to create a server named "Time Server".
- Each function decorated with `@mcp.tool()` becomes a callable tool. The **docstring becomes the tool description**, which the planner LLM reads to choose a tool.
- Tools:
  | Tool | Does |
  |---|---|
  | `current_time()` | Returns the date and time as `YYYY-MM-DD HH:MM:SS` |
  | `roll_dice()` | Returns a random number 1–6 |
  | `generate_password()` | Returns a random 12-character password using the `secrets` module (cryptographically secure) |
- `mcp.run()` starts it on **stdio** transport (talks through stdin/stdout).

> **Interview point:** Good docstrings matter because they are the LLM's only description of the tool.

### 5.2 `mcp_client.py`: talks to the MCP server

| Function | Purpose |
|---|---|
| `connect()` | Creates `Client("server.py")`, manually enters its async context (`__aenter__`), and returns it. FastMCP launches the server subprocess. |
| `disconnect(client)` | Calls `__aexit__` to shut the connection down cleanly. |
| `discover_tool(client)` | `client.list_tools()` returns the tools' names, descriptions and schemas. |
| `execute_tool(client, tool_name, args=None)` | `client.call_tool(name, args)` runs a tool. `args` defaults to `{}`. |

> **Why `__aenter__`/`__aexit__` by hand?** Normally you'd write `async with Client(...)`. Doing it manually keeps the connection open across functions, but you must remember to disconnect.

### 5.3 `state.py`: the agent's memory

`create_state(user_request, max_steps=5)` returns a dict:

```python
{
  "user_request": "...",
  "tasks": [],            # [{"task": "...", "status": "pending|completed"}]
  "current_task": None,   # the task being worked on
  "current_step": 0,      # loop counter
  "max_steps": 5,         # safety limit
  "actions": [],          # tools called so far
  "observations": [],     # [{"step", "action", "observation"}]
  "results": [],          # intermediate outputs
  "finished": False,
  "final_answer": ""
}
```

Helper functions:

| Function | What it does |
|---|---|
| `add_task(state, task)` | Appends a task with status `pending` |
| `complete_task(state, task)` | Sets the matching task's status to `completed` |
| `get_pending_tasks(state)` | Returns names of tasks still pending |
| `all_tasks_completed(state)` | `True` if every task is completed |
| `add_action(state, action)` | Logs which tool was called |
| `record_observation(state, action, observation)` | Stores step number, tool and output |
| `add_result(state, result)` | Stores an intermediate result |
| `next_step(state)` | Increments `current_step` |
| `can_continue(state)` | `True` if not finished and `current_step < max_steps` |
| `finish(state, answer)` | Saves the final answer and sets `finished = True` |

> **Interview point:** A single state dict is the *single source of truth*. Every component reads or writes it, so the planner always sees full history.

### 5.4 `task_planner.py`: the task decomposer

- `decompose_task(user_request)` makes **one LLM call** with the prompt "Break the request into short tasks, in order, one per line, no numbering, no explanation".
- It splits the response by lines, strips whitespace, drops empty lines, and returns a Python list of strings.
- This is the **high-level plan** made upfront (the "planning" in "agent planning").

### 5.5 `planner.py`: the step-by-step decision maker

- `build_tool_descriptions(tools)` loops through the MCP tool objects and creates a text block with each tool's name and description for the prompt.
- `planner(state, tools)` builds a big prompt containing the user request, tasks with statuses, completed actions, observations, intermediate results and tool descriptions.
- **Rules in the prompt:** pick ONE pending task, pick the best tool, don't repeat completed tasks, use observations, reconsider on failure, return `FINISH` when everything is done.
- **Required output format** (so code can parse it):
  ```
  TASK: <task>
  TOOL: <tool>
  ```
  or the single word `FINISH`.

> **Two levels of planning:** `task_planner` = *what* needs doing overall (once). `planner` = *what next*, using fresh observations (every step). This is the **adaptive plan-and-execute** pattern.

### 5.6 `executor.py`: runs one action

`execute_action(action, state, client)`:
1. Calls `execute_tool(client, action)` (the MCP call).
2. MCP returns a result object. If it has `.content`, it returns `content[0].text`. Otherwise it returns `str(result)`.

It converts the MCP result into a plain string the rest of the code can use.

### 5.7 `loop.py`: the agent loop (the heart)

- `parse_decision(decision)`: reads the planner's text line by line. A line starting with `TASK:` gives the task and a line starting with `TOOL:` gives the tool. It returns `(task, tool)`.
- `run_agent_loop(user_request, planner, execute_action, format_answer, tools, client)`:
  - Takes the planner, executor and answer function as **parameters** (dependency injection), so they are easy to swap or mock in tests.
  - Creates state, decomposes the task, prints the plan.
  - Loops `while can_continue(state)` through plan, parse, act, observe, update.
  - Guards:
    - `FINISH` → answer and break
    - Invalid format → log "Invalid Planner decision", skip to the next step
    - `max_steps` → stops infinite loops, then still produces an answer

### 5.8 `answer.py`: final response writer

`format_answer(state)` sends the request, tasks, actions, observations and results to the LLM. It asks for a natural, concise answer that does **not** mention planner, tools, MCP or internal state.

### 5.9 `runner.py`: the entry point

`main()` (async) wires everything up:

```
connect → discover_tool → print tools → input → run_agent_loop → print answer → disconnect
```

It runs via `asyncio.run(main())` because MCP calls are **async**.

### 5.10 `test_state.py` and `test_task_planner.py`: manual tests

- `test_state.py` exercises the state helpers with fake data (create state, add an action, record an observation, finish) and prints the state at each stage. No LLM needed.
- `test_task_planner.py` calls `decompose_task()` on a sample request and prints the tasks. It needs the LLM running.
- This shows **bottom-up development**: state first, then the task planner, then the loop, so each part is tested in isolation.

### 5.11 `.env`

Holds `BASE_URL`, `API_KEY` and `MODEL`. Loaded by `python-dotenv`. The project uses **Ollama** (local) at `http://localhost:11434/v1` with model `qwen3:4b`. Ollama exposes an **OpenAI-compatible API**, so the standard `openai` library works unchanged. Never commit API keys.

---

## 6. Key concepts and the vocabulary interviewers expect

| Term | Simple meaning |
|---|---|
| **Agent loop / ReAct** | Repeat: Reason → Act (call tool) → Observe → Reason... |
| **Plan-and-Execute** | Make a plan first, then execute step by step, adjusting as needed |
| **Task decomposition** | Splitting a big goal into small, ordered tasks |
| **Tool calling** | The LLM chooses an external function to run |
| **MCP (Model Context Protocol)** | An open standard for exposing tools and data to LLMs. A server offers tools and a client discovers and calls them |
| **FastMCP** | A Python library to build MCP servers and clients quickly |
| **State / memory** | The data structure that carries context between steps |
| **Observation** | The result a tool returns after an action |
| **Stop condition** | `FINISH` or `max_steps`, to prevent infinite loops |
| **stdio transport** | Client and server communicate via a subprocess's stdin/stdout |
| **Dependency injection** | Passing functions in as arguments (`planner`, `execute_action`) instead of hardcoding |
| **Async/await** | Non-blocking I/O, needed for MCP client calls |
| **Prompt engineering** | Writing strict, structured prompts so output is parseable |

---

## 7. Likely interview questions and model answers

**Q1. Explain your agent architecture.**
Use the pitch in section 1 and walk through the diagram in section 3.

**Q2. Why two planners (`task_planner` and `planner`)?**
The task planner gives the overall roadmap once. The step planner re-evaluates after every observation, so it can handle failures, pick the right tool and know when to stop. A static plan alone can't adapt.

**Q3. How do you prevent infinite loops?**
`max_steps` in state (default 5) checked by `can_continue()`. There is also an explicit `FINISH` signal, and invalid decisions still advance the step counter.

**Q4. What if the LLM returns the wrong format?**
`parse_decision` returns `None` for task or tool. The loop records "Invalid Planner decision", increments the step and retries. Improvements: use JSON or function-calling mode, a retry with a corrective message, or regex validation.

**Q5. What if a tool fails?**
If the observation starts with "error", the task is not marked complete and a note "previous action failed, reconsider" is added to results. The planner sees this on the next step.

**Q6. Why MCP instead of hardcoding functions?**
It decouples tools from the agent. Any MCP server can be plugged in, tools are discovered dynamically, and the same server works with other clients (Claude Desktop, IDEs).

**Q7. Why keep state in a dict?**
It is simple, serialisable (can be saved or logged) and transparent. For production, I'd use a dataclass or Pydantic model for type safety, and persist it to a database for resumability.

**Q8. How does the LLM know which tools exist?**
`discover_tool` fetches the tools from the MCP server and `build_tool_descriptions` injects their names and docstrings into the planner prompt.

**Q9. Why a local model (Ollama)?**
Privacy, zero cost and offline use. The OpenAI-compatible endpoint means I can switch to a hosted model by changing only `.env`. Trade-off: small models like a 4B model are slower and less reliable at following strict formats.

**Q10. What are the limitations and how would you improve it?**
- `execute_action` calls tools with **no arguments**, so tools needing parameters (e.g. dice sides) won't work. Fix: have the planner output JSON args and pass them through.
- Text parsing is fragile. Use native tool/function calling or structured JSON output.
- No retry limit per task, no timeouts on LLM calls.
- Tasks are matched by exact string, so if the planner rephrases a task, `complete_task` won't find it. Use task IDs.
- No persistent memory or conversation history.
- Tasks run sequentially. Independent tasks could run in parallel.
- Add logging, tracing and evaluation tests.

**Q11. How would you test it?**
Unit-test `state.py` (pure functions). Test `decompose_task` and `planner` with a mocked LLM client. Test `run_agent_loop` by injecting fake `planner` and `execute_action` functions, which is why they are parameters. Then do end-to-end runs.

**Q12. Difference between ReAct and Plan-and-Execute?**
ReAct decides one step at a time with no upfront plan. Plan-and-Execute plans first, then executes. This project is a **hybrid**: it plans upfront, but re-decides each step based on observations.

---

## 8. Bugs fixed during development (great "debugging story" for interviews)

| Bug | Lesson |
|---|---|
| Passed the OpenAI client where the MCP client was needed (`'OpenAI' object has no attribute 'list_tools'`) | Name clients clearly (`llm_client`, `mcp_client`) to avoid mixing them up |
| `state["result"]` vs `state["results"]` key mismatch | Use constants or a dataclass to avoid typo bugs |
| `item["Status"]` vs `"status"` | Dict keys are case-sensitive |
| `startwith` typo and `startswith[...]` | Linters or type checkers catch these |
| `break` / `continue` outside the `if`, so the loop exited after step 1 | In Python, indentation is the logic |
| Loop-update code placed outside the `while` | Check indentation after edits |
| Invalid message role `"User"` | The API expects lowercase `user` |
| Duplicate `format_answer` in `runner.py` shadowed the imported one | Avoid defining a function with the same name as an import |

---

## 9. How to run

```bash
cd day10/agent
source ../../.venv/bin/activate    # or your venv
ollama serve                       # make sure Ollama is running with the model pulled
python3 test_state.py              # no LLM needed
python3 test_task_planner.py       # needs the LLM
python3 runner.py                  # full agent
```

Try: `generate a password and tell me the current time`, or `roll the dice`.

---

## 10. Quick revision cheat sheet

```
runner.py    → entry: connect, discover, input, run loop, print, disconnect
loop.py      → while can_continue: plan → parse → execute → record → update
task_planner → LLM splits request into ordered tasks (once)
planner.py   → LLM picks TASK + TOOL or FINISH (each step)
executor.py  → calls MCP tool, returns text
mcp_client.py→ connect / disconnect / list_tools / call_tool
server.py    → FastMCP tools: current_time, roll_dice, generate_password
state.py     → shared memory dict + helper functions
answer.py    → LLM writes the final natural-language reply
.env         → BASE_URL, API_KEY, MODEL (Ollama, qwen3:4b)
```

**Flow in six words:** Decompose → Plan → Act → Observe → Repeat → Answer.
