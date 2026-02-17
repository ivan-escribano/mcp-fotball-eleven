# Actualizado - Exports from web_search module
from services.web_search import (
    search_player_context, PLAYER_CONTEXT_PROMPT,
    search_team_context, TEAM_CONTEXT_PROMPT,
    SEARCH_PLAYERS_PROMPT,
    search_player_highlights,
)

__all__ = [
    "search_player_context", "PLAYER_CONTEXT_PROMPT",
    "search_team_context", "TEAM_CONTEXT_PROMPT",
    "SEARCH_PLAYERS_PROMPT",
    "search_player_highlights",
]
