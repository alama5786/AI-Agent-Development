# Day 04: Tools (Giving the Assistant "Hands")

**Theme:** let the assistant do things an LLM can't do alone (get the real time, roll a dice, generate a secure password) by running ordinary Python functions.

## 1. Pitch

> "On day 4 I introduced tools. I wrote plain Python functions and a small `tool_manager` that routes the user's input to the right function using keyword matching. This is the simplest form of tool use, and it sets up the later LLM-driven planner."

## 2. Files

| File | Purpose |
|---|---|
| `tools.py` | The actual tool functions |
| `tool_manager.py` | `execute_tool(user_input)`: decides which tool (if any) to run |
| `assistant.py` | The chat app. It checks for a tool first and only then talks to the LLM |
| `test_tool.py` | Calls each tool directly to verify it works |
| `test_tool_manager.py` | Tests the routing with sample inputs, including an unknown command |

## 3. The tools (`tools.py`)

| Function | Behaviour |
|---|---|
| `get_current_time()` | Returns `dd-mm-YYYY hh:mm:ss AM/PM` using `datetime.now()` |
| `roll_dice(sides=6)` | `random.randint(1, sides)` |
| `generate_password(length=12)` | Picks `length` characters from letters, digits and punctuation using `secrets.choice` (cryptographically secure, unlike `random`) |

## 4. Flow

```
user input
   │
   ▼
execute_tool(user_input)       <- keyword routing
   ├─ contains "time"     -> get_current_time()
   ├─ contains "dice"     -> roll_dice()
   ├─ contains "password" -> asks for length -> generate_password(n)
   └─ otherwise           -> None  (so the assistant would talk to the LLM)
```

`assistant.py` calls `execute_tool` first. If a result comes back, it prints it and skips the LLM.

## 5. Key concepts

| Concept | Meaning |
|---|---|
| **Tool / function** | A normal function the program can run on request |
| **Routing** | Choosing which tool fits a request. Here it is rule-based (`if "time" in text`) |
| **`secrets` vs `random`** | `secrets` is for security-sensitive values like passwords and tokens |
| **Separation of concerns** | Tools in one file, routing in another, UI in a third |
| **Test scripts** | Small scripts that run each piece in isolation |

## 6. Run it

```bash
cd 4_tool_basics
python3 test_tool.py
python3 test_tool_manager.py
python3 assistant.py
```

## 7. Interview Q&A

**Q: Why can't the LLM just tell me the time?**
It has no live data. A tool fetches facts from the real world and the app passes them in.

**Q: Weakness of keyword routing?**
It is brittle. "What time does the shop open?" triggers the time tool, and "sometimes" contains "time". That is why day 7 lets the LLM choose the tool.

**Q: Why `secrets` for passwords?**
`random` is predictable (a pseudo-random generator). `secrets` uses the OS's secure randomness.

**Q: Why write `test_*.py` files?**
To check each layer independently before wiring it into the app, which makes debugging much easier.

## 8. Known issues in this folder (good "what I'd fix" answers)
- In `assistant.py` the `break` after the exit check is **not indented under the `if`**. Any input that isn't a tool command ends the loop before reaching the LLM. It should sit inside `if user_input.lower() in ["exit","quit"]:`.
- `tool_manager.execute_tool` calls `input()` itself (for the password length), mixing UI with logic.
- The dice always has 6 sides in the router, even though `roll_dice` supports `sides`.
- The tool check happens *before* the exit check.

## 9. Cheat sheet
```
tools.py        -> real functions (time, dice, password)
tool_manager.py -> keyword router, returns text or None
assistant.py    -> try tool first, else LLM
```
