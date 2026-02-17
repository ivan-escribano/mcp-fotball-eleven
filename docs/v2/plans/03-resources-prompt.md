# Spec 3 — Implementation Plan

## Important note

Both `@mcp.resource()` and `@mcp.prompt()` don't work through `mcp-remote` bridge in Claude Desktop. See `docs/specs-v2/explanation/why-mcp-prompt-not-working.md` for details.

They WILL work with: `mcp dev`, Cursor, and future Claude Desktop versions with native HTTP.

Our existing workaround (description + instructions in return value) already covers Claude Desktop.

---

## Spec 3A: Resources

Add example queries, stats glossary, and available leagues as MCP resources in `main.py`.

### Step 1: Add example query resources

4 resources with example `search_players` inputs:
- `mcp-eleven://examples/clinical-striker`
- `mcp-eleven://examples/creative-midfielder`
- `mcp-eleven://examples/ball-playing-cb`
- `mcp-eleven://examples/pressing-forward`

### Step 2: Add stats glossary resource

- `mcp-eleven://stats-glossary` — What each stat means + what values are considered good.

### Step 3: Add available leagues resource

- `mcp-eleven://available-leagues` — Exact league names from DB + current season.

**No new files, no new dependencies. Everything in `main.py`.**

---

## Spec 3B: Prompt

### Step 4: Add scouting report prompt

One `@mcp.prompt()` in `main.py` — covers all 3 tools (search_players, get_player_context, get_team_context).

**No new files, no new dependencies.**

---

## Summary

| Step | What | Where |
|------|------|-------|
| 1 | 4 example query resources | main.py |
| 2 | Stats glossary resource | main.py |
| 3 | Available leagues resource | main.py |
| 4 | Scouting report prompt | main.py |
