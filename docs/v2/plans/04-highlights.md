# Spec 4 — Video Highlights Implementation Plan

## What

New tool `get_player_highlights` that searches highlight videos for a player using Tavily with `include_domains` filtering for video platforms.

## Steps

| Step | What | Where |
|------|------|-------|
| 1 | Add `search_player_highlights` function | services/web_search/search.py |
| 2 | Add video config (domains) | services/web_search/config.py |
| 3 | Update exports | services/web_search/__init__.py + services/__init__.py |
| 4 | Register `get_player_highlights` tool | main.py |

No new dependencies — reuses Tavily from Spec 1.
