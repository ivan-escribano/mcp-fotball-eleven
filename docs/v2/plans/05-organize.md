# Spec 5 — Project Organization

## Current Structure

```
mcp-eleven/
├── main.py                     ← Entry point + 4 tools + middleware (too much)
├── config/
│   ├── settings.py
│   ├── database.py
│   └── leagues.py
├── model/
│   ├── player.py
│   ├── filters.py
│   └── api_key.py
├── db/
│   └── database.py
├── auth/
│   └── middleware.py
├── services/
│   └── web_search/
│       ├── config.py
│       ├── prompts.py
│       └── search.py
├── utils/
│   └── normalize_player_stats.py
├── scripts/
├── data/
├── docs/
└── .testing/
```

**Problem:** `main.py` does too many things — creates the MCP instance, defines middleware, registers 4 tools, and runs the server. As we add more tools, this file will keep growing.

---

## Proposed Structure

```
mcp-eleven/
├── main.py                     ← Clean entry point (only imports + run)
├── server.py                   ← MCP instance + middleware (created)
├── tools/                      ← NEW: Each tool in its own file
│   ├── __init__.py
│   ├── search_players.py
│   ├── player_context.py
│   ├── team_context.py
│   └── player_highlights.py
├── config/                     ← No changes
│   ├── settings.py
│   ├── database.py
│   └── leagues.py
├── model/                      ← No changes
│   ├── player.py
│   ├── filters.py
│   └── api_key.py
├── db/                         ← No changes
│   └── database.py
├── auth/                       ← No changes
│   └── middleware.py
├── services/                   ← No changes
│   └── web_search/
│       ├── config.py
│       ├── prompts.py
│       └── search.py
├── utils/                      ← No changes
├── scripts/                    ← No changes
├── tests/                      ← Renamed from .testing/
├── data/
└── docs/
```

---

## What Changes

| File | Action | Why |
|------|--------|-----|
| `server.py` | **Create** | MCP instance + middleware in one place |
| `tools/` | **Create** | Each tool gets its own file |
| `main.py` | **Simplify** | Just imports tools and runs the server |
| `.testing/` | **Rename** to `tests/` | Python standard convention |

---

## How It Works

### server.py — MCP instance + middleware

```python
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request
from mcp import McpError
from mcp.types import ErrorData
from auth import validate_request

mcp = FastMCP("MCPEleven")

class ApiKeyMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        request = get_http_request()
        if request and not validate_request(request):
            raise McpError(ErrorData(code=-32001, message="Invalid or missing API key."))
        return await call_next(context)

mcp.add_middleware(ApiKeyMiddleware())
```

### tools/search_players.py — One tool per file

```python
from server import mcp
from db.database import get_players
from model import PlayerStatsFilters
from services import SEARCH_PLAYERS_PROMPT

@mcp.tool(description=SEARCH_PLAYERS_PROMPT)
def search_players(filters: PlayerStatsFilters) -> list[dict]:
    """Search football players based on statistical filters."""
    try:
        return get_players(filters)
    except (ValueError, KeyError, TypeError) as e:
        return [{"error": str(e)}]
```

### tools/__init__.py — Import all tools so decorators register

```python
from tools.search_players import search_players
from tools.player_context import get_player_context
from tools.team_context import get_team_context
from tools.player_highlights import get_player_highlights

__all__ = [
    "search_players",
    "get_player_context",
    "get_team_context",
    "get_player_highlights",
]
```

### main.py — Clean entry point

```python
from server import mcp
from tools import *  # Registers all tools via decorators
from config import HOST, PORT

# Health check (no auth)
from starlette.requests import Request
from starlette.responses import JSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    return JSONResponse({"status": "healthy"})

if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
```

---

## Why This Pattern

Based on how real MCP servers are built:

- **GitHub MCP Server** — `tools/` folder with `repository_tools.py`, `issue_tools.py`, `pr_tools.py`
- **Official MCP Servers** — Each server has its own module under `src/`
- **FastMCP examples** — Separate `server.py` for the instance, tools import it

**Benefits:**
- Adding a new tool = create one file in `tools/`, add one import in `__init__.py`
- Each tool file is self-contained: imports what it needs, defines one tool
- `main.py` stays clean no matter how many tools we add
- Easy to test individual tools in isolation

---

## What Stays The Same

- `config/`, `model/`, `db/`, `auth/`, `services/`, `utils/`, `scripts/` — no changes needed
- These folders are already well organized
- The `services/web_search/` pattern (config + prompts + search) works well

---

## Docs Organization

### Proposed docs (versioned)

```
docs/
├── DOCS_GUIDE.md                    ← How to structure docs for any version
│
├── v1/                              ← Original version
│   ├── specs/
│   ├── plans/
│   ├── explanations/
│   ├── improvements/
│   ├── images/
│   └── changelog.md
│
├── v2/                              ← Current work
│   ├── specs/                       (what to build)
│   │   └── mcp-eleven-specs-v2.md
│   ├── plans/                       (how to build each spec)
│   │   ├── 01-player-context.md
│   │   ├── 02-team-context.md
│   │   ├── 03-resources-prompt.md
│   │   ├── 04-highlights.md
│   │   ├── 05-organize.md
│   │   └── 06-best-practices.md
│   ├── explanations/                (deep dives, how things work)
│   │   ├── search-player-context.md
│   │   ├── mcp-prompts.md
│   │   └── why-mcp-prompt-not-working.md
│   ├── improvements/                (what changed and why)
│   │   └── 01-search-improvements.md
│   ├── images/                      (diagrams, screenshots, demos)
│   │   ├── diagrams/
│   │   └── demo/
│   └── changelog.md                 (log of everything done in v2)
│
├── v3/                              ← Future work (same structure)
│   ├── specs/
│   ├── plans/
│   ├── explanations/
│   ├── improvements/
│   ├── images/
│   └── changelog.md
```

### DOCS_GUIDE.md (root of docs)

A guide that explains how to create a new version folder. Every version follows the same 5 folders:

| Folder | What goes here | Naming |
|--------|---------------|--------|
| `specs/` | Feature specifications | `<feature-name>.md` |
| `plans/` | Implementation plans for each spec | `<NN>-<feature-name>.md` |
| `explanations/` | Deep dives on how things work | `<topic>.md` |
| `improvements/` | Changes, experiments, what changed and why | `<NN>-<description>.md` |
| `images/` | Diagrams, screenshots, demo videos | Subfolders as needed |

Plus a `changelog.md` at the root of each version.

---

## Implementation Steps

1. Create `server.py` — extract MCP instance + middleware from `main.py`
2. Create `tools/` folder with 4 tool files
3. Update `main.py` to just import and run
4. Rename `.testing/` to `tests/`
5. Reorganize `docs/` into versioned structure
6. Create `docs/DOCS_GUIDE.md`
7. Test everything works