# Actualizado - Exports from web_search module
from services.web_search.search import search_player_context, search_team_context, search_player_highlights
from services.web_search.prompts import (
    PLAYER_CONTEXT_PROMPT, TEAM_CONTEXT_PROMPT, SEARCH_PLAYERS_PROMPT,
)

__all__ = [
    "search_player_context", "PLAYER_CONTEXT_PROMPT",
    "search_team_context", "TEAM_CONTEXT_PROMPT",
    "SEARCH_PLAYERS_PROMPT",
    "search_player_highlights",
]
