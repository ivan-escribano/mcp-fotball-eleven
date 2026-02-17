# Why @mcp.prompt doesn't work with Claude Desktop + mcp-remote

## The problem

You register a prompt in your server:

```python
@mcp.prompt
def scouting_report() -> str:
    return "Present data as a scouting report..."
```

The server exposes it correctly. But when you open Claude Desktop, the prompt doesn't appear in the "+" menu.

## Why it happens

Your Claude Desktop config uses `mcp-remote` as a bridge:

```json
{
  "mcp-eleven": {
    "command": "npx",
    "args": [
      "mcp-remote@latest",
      "http://localhost:8000/mcp?api_key=sk_xxx",
      "--allow-http"
    ]
  }
}
```

The problem is the chain of communication:

```
Claude Desktop  <-->  mcp-remote (stdio bridge)  <-->  Your server (HTTP)
```

1. Claude Desktop only speaks **stdio** (it launches servers as child processes)
2. Your server speaks **HTTP**
3. `mcp-remote` sits in the middle translating between the two

`mcp-remote` translates **tools** correctly — Claude Desktop sees `search_players` and `get_player_context` fine. But **prompts and resources** don't always get forwarded properly through this bridge. It's a known limitation of `mcp-remote`.

## Who does it affect?

- **Claude Desktop** — Uses stdio, needs `mcp-remote` bridge. Prompts don't show.
- **Cursor / VSCode** — Connect via HTTP directly. Prompts *may* work, but support varies by client.
- **`mcp dev` (FastMCP inspector)** — Connects directly. Prompts work fine here.

## The workaround we use

Instead of relying on `@mcp.prompt`, we put the instructions in two places:

### 1. In the `description` parameter of `@mcp.tool`

```python
@mcp.tool(description=PLAYER_CONTEXT_PROMPT)
def get_player_context(player_name: str, team: str = None) -> dict:
```

The LLM reads the tool description to understand what it does. If we put formatting instructions here, the LLM knows *how* to present the data before it even calls the tool.

### 2. In the return value (as `instructions` key)

```python
return {
    "instructions": PLAYER_CONTEXT_PROMPT,
    **search_player_context(player_name, team),
}
```

This guarantees the LLM receives the instructions together with the data, every single time. Even if it ignores the tool description, the instructions are right there in the response.

### Why both?

- `description` → The LLM reads it **before** calling the tool (helps it decide when to use it)
- `instructions` in return → The LLM reads it **after** getting the data (helps it format the output)

Belt and suspenders. Works on every client, no matter how they connect.

## Will this be fixed?

Maybe. It depends on:
- `mcp-remote` adding proper support for prompts/resources forwarding
- Claude Desktop adding native HTTP transport (so you don't need `mcp-remote` at all)

Both are being discussed in the community but there's no timeline. For now, the workaround is solid and works everywhere.

## Sources

- https://github.com/jlowin/fastmcp/discussions/813 — Claude Desktop not seeing resources/prompts
- https://gofastmcp.com/integrations/claude-desktop — FastMCP + Claude Desktop integration docs