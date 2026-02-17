# Spec 6 — Best Structure Practices for MCP Servers

## Sources

Based on how real MCP servers are built:
- [GitHub MCP Server](https://github.com/github/github-mcp-server) — tools/ folder pattern
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers) — src/ layout
- [FastMCP docs](https://gofastmcp.com/deployment/server-configuration) — server configuration
- [Python Packaging Authority](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — project layout

---

## 1. Separate the MCP Instance from the Entry Point

**Bad** — everything in one file:
```python
# main.py
mcp = FastMCP("MyServer")

@mcp.tool
def my_tool(): ...

class MyMiddleware(Middleware): ...
mcp.add_middleware(MyMiddleware())

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Good** — instance in its own file:
```python
# server.py
mcp = FastMCP("MyServer")

# main.py
from server import mcp
from tools import *
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Why:** Every tool file needs to import `mcp` to register itself. If `mcp` lives in `main.py`, you get circular imports. A standalone `server.py` solves this cleanly.

---

## 2. One Tool Per File

**Bad** — all tools in main.py:
```python
# main.py (grows forever)
@mcp.tool
def search_players(): ...

@mcp.tool
def get_player_context(): ...

@mcp.tool
def get_team_context(): ...

@mcp.tool
def get_player_highlights(): ...
```

**Good** — each tool in its own module:
```
tools/
├── __init__.py              # Imports all tools (registers decorators)
├── search_players.py        # One tool, its imports, its logic
├── player_context.py
├── team_context.py
└── player_highlights.py
```

**Why:**
- Each file is self-contained and easy to understand
- Adding a tool = create file + add one import
- Easy to test in isolation
- This is what GitHub MCP Server does (`repository_tools.py`, `issue_tools.py`, `pr_tools.py`)

---

## 3. Tools Import the Server, Not the Other Way Around

```python
# tools/search_players.py
from server import mcp          # Tool imports server
from model import PlayerStatsFilters

@mcp.tool
def search_players(filters: PlayerStatsFilters) -> list[dict]:
    ...
```

```python
# tools/__init__.py
from tools.search_players import search_players    # This triggers @mcp.tool registration
from tools.player_context import get_player_context
```

```python
# main.py
from server import mcp
from tools import *    # All tools get registered
```

**Why:** The `@mcp.tool` decorator registers the function when the file is imported. You just need to make sure all tool files get imported before `mcp.run()`.

---

## 4. Keep Services Separate from Tools

```
tools/                        # MCP interface layer
├── player_context.py         # Calls services, handles errors, returns response

services/                     # Business logic layer
└── web_search/
    ├── search.py             # Actual Tavily search logic
    ├── prompts.py            # LLM instructions
    └── config.py             # Search categories, domains
```

**Tool file** = thin wrapper (call service, catch errors, return result):
```python
@mcp.tool(description=PLAYER_CONTEXT_PROMPT)
def get_player_context(player_name: str, team: str = None) -> dict:
    try:
        return {"instructions": PLAYER_CONTEXT_PROMPT, **search_player_context(player_name, team)}
    except Exception as e:
        return {"error": str(e)}
```

**Service file** = actual logic (search, transform, process):
```python
def search_player_context(player_name: str, team: str = None) -> dict:
    base_query = f"{player_name} {team}" if team else player_name
    context = {}
    for category, cat_config in PLAYER_SEARCH_CATEGORIES.items():
        result = tavily_client.search(...)
        context[category] = result.get("results", [])
    return {"player": player_name, "team": team, "context": context}
```

**Why:** Tools are the interface (what the LLM sees). Services are the implementation (what actually happens). If you change how search works, you only touch `services/`. If you change what the LLM sees, you only touch `tools/`.

---

## 5. Config by Domain, Not by Type

**Bad** — one giant config file:
```python
# config.py
HOST = "0.0.0.0"
PORT = 8000
DB_URL = "sqlite:///data/mcp.db"
TAVILY_API_KEY = "..."
PLAYER_SEARCH_CATEGORIES = {...}
VIDEO_DOMAINS = [...]
LEAGUES = [...]
```

**Good** — config split by domain:
```
config/
├── settings.py       # HOST, PORT, APIKEY_SALT, TAVILY_API_KEY
├── database.py       # DB_URL, DATA_DIR, DB_NAME
└── leagues.py        # LEAGUES_TO_LOAD, SofascoreLeague

services/web_search/
├── config.py         # PLAYER_SEARCH_CATEGORIES, TEAM_SEARCH_CATEGORIES, VIDEO_DOMAINS
```

**Why:** Search categories belong with the search code, not in global config. Each module owns its own configuration.

---

## 6. Prompts Live Next to the Code That Uses Them

**Bad** — prompts in a global folder:
```
prompts/
├── player_context.txt
├── team_context.txt
└── search_players.txt
```

**Good** — prompts next to their service:
```
services/web_search/
├── prompts.py        # PLAYER_CONTEXT_PROMPT, TEAM_CONTEXT_PROMPT, SEARCH_PLAYERS_PROMPT
├── search.py         # Uses the prompts
└── config.py
```

**Why:** When you change how search works, you probably need to update the prompt too. Having them in the same folder makes this obvious.

---

## 7. Middleware Stays with Auth

```
auth/
├── __init__.py
└── middleware.py      # API key validation + MCP middleware class
```

Or in `server.py` if it's simple enough (one class). The point is: authentication logic should be in one place, not scattered across files.

---

## 8. Tests Mirror the Source Structure

```
tests/
├── test_search_players.py       # Tests tools/search_players.py
├── test_player_context.py       # Tests tools/player_context.py
├── test_http_local.py           # Integration tests
└── test_http_production.py      # Production smoke tests
```

**Why:** Easy to find the test for any file. Convention: `tests/test_<module>.py`.

---

## 9. Exports Flow Upward

Each `__init__.py` exports what the layer above needs:

```python
# services/web_search/__init__.py — exports for tools
from services.web_search.search import search_player_context, search_team_context, search_player_highlights
from services.web_search.prompts import PLAYER_CONTEXT_PROMPT, TEAM_CONTEXT_PROMPT, SEARCH_PLAYERS_PROMPT

# services/__init__.py — re-exports for convenience
from services.web_search import search_player_context, PLAYER_CONTEXT_PROMPT, ...

# tools/player_context.py — imports from services
from services import search_player_context, PLAYER_CONTEXT_PROMPT
```

**Why:** Clean import paths. Tool files don't need to know the internal structure of services.

---

## 10. The Ideal MCP Server Layout

```
my-mcp-server/
├── main.py                  # Entry point: import tools, run server
├── server.py                # MCP instance + middleware
├── tools/                   # One file per tool
│   ├── __init__.py
│   └── <tool_name>.py
├── services/                # Business logic by domain
│   └── <domain>/
│       ├── config.py
│       ├── prompts.py
│       └── <logic>.py
├── config/                  # Global config (env, db, etc.)
├── model/                   # Data models (Pydantic, SQLModel)
├── db/                      # Database layer
├── auth/                    # Authentication
├── utils/                   # Shared utilities
├── tests/                   # Test files
├── scripts/                 # CLI scripts
├── docs/                    # Documentation
├── data/                    # Local data files
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

**Rules of thumb:**
- `main.py` should be under 15 lines
- `server.py` should be under 30 lines
- Each tool file should be under 30 lines
- If a folder has only one file, consider if it needs to be a folder
- If a file has more than 100 lines, consider splitting it
