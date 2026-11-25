# Day 07: LLM-Based Tool Planner (the LLM Chooses the Tool)

**Theme:** replace brittle keyword routing with an **LLM planner** that reads the request and decides which tool to use.

## 1. Pitch

> "On day 7 I added a planner. A dedicated LLM call receives the user request plus a list of available tools and replies with just the tool name, or `none`. The assistant runs that tool, then makes a second LLM call to turn the raw tool result into a natural reply. This is the first real 'agentic' step: the model decides, the code executes."

## 2. Files

| File | Purpose |
|---|---|
| `planner.py` | `choose_tool(user_request)`: asks the LLM to pick a tool name |
| `assistant.py` | Main app: plan, execute, respond |
| `tools.py` | `get_current_time`, `roll_dice`, `generate_password` (plus `read_text_file`, unused here) |
| `test_planner.py` | Checks that the planner picks the right tool for three sample requests |
| `test_tool.py` | Calls each tool directly |

## 3. Flow

```
user input
   │
   ▼
choose_tool()  ── LLM call #1 (planner) ──►  "get_current_time" | "roll_dice" | "generate_password" | "none"
   │
   ▼
if/elif dispatch in assistant.py  -> run the matching Python function
   │ (none -> "I'm sorry, I cannot assist with that request.")
   ▼
LLM call #2: prompt = user request + tool chosen + tool result
   │
   ▼
natural-language answer printed
```

### `planner.py` in detail
- The prompt lists each tool with a one-line description.
- It instructs: "respond with the tool name only, or `none`".
- The reply is `.strip().lower()`-ed so it compares cleanly with the tool names.

## 4. Key concepts

| Concept | Meaning |
|---|---|
| **Planner / router** | A component (here an LLM call) that decides *what to do next* |
| **Tool description** | The text the LLM uses to pick a tool, so it must be clear |
| **Two-call pattern** | Call 1 chooses the action. Call 2 turns the result into a human answer |
| **Constrained output** | Telling the model to answer with one word makes parsing easy |
| **Fallback (`none`)** | Always give the model a "no tool fits" option |

## 5. Run it

```bash
cd 7_llm_tool_planner
python3 test_planner.py     # prints the chosen tool for 3 requests
python3 assistant.py        # try: "roll a dice", "what time is it", "make me a password"
```

## 6. Interview Q&A

**Q: Why use an LLM to pick tools instead of `if "time" in text`?**
It understands intent and phrasing ("what's the hour?"), and it scales to many tools without writing rules for each.

**Q: What can go wrong?**
The model may add extra words (`Tool: roll_dice`), pick a non-existent tool, or hallucinate. Mitigations: validate against a whitelist, retry, use JSON or native function calling, and use `temperature=0`.

**Q: Why is there a `none` option?**
Without it, the model is forced to pick a tool even for unrelated requests.

**Q: Why a second LLM call?**
Raw tool output ("4") isn't a friendly answer. The second call phrases it in context.

**Q: Cost of this design?**
Two LLM calls per request, so more latency and tokens.

## 7. Known issues
- `planner.py` sends `"role": "SYSTEM"` in uppercase. The standard role is lowercase `system`, and some servers reject it.
- `generate_password` uses a hard-coded length of 12, because the planner doesn't extract arguments.
- No whitelist validation. An unexpected planner reply silently falls into the "cannot assist" branch.
- No conversation memory in `assistant.py` (each request is independent).
- Tool metadata is duplicated in the prompt text and in the if/elif chain. Adding a tool means editing both.

## 8. Cheat sheet
```
choose_tool(request) -> tool name -> run function -> LLM turns result into a reply
Planner = decide.  Code = execute.  LLM again = explain.
```
