from server import mcp
from db.database import get_players
from model import PlayerStatsFilters
from services import SEARCH_PLAYERS_PROMPT


@mcp.tool(description=SEARCH_PLAYERS_PROMPT)
def search_players(filters: PlayerStatsFilters) -> list[dict]:
    """
    Search football players based on statistical filters.

    Use this tool to find players matching specific criteria like:
    - Goals, assists, expected goals (xG)
    - Passing accuracy, key passes, crosses
    - Tackles, interceptions, clearances
    - Dribbles, duels won
    - Goalkeeper stats (saves, claims, etc.)

    All filters are optional. Use min_ prefix for minimum values,
    max_ prefix for maximum values. Text fields support partial matching.

    Examples:
    - Top scorers: min_goals=15
    - Creative midfielders: min_assists=8, min_key_passes=40
    - Solid defenders: min_tackles=50, max_dribbled_past=20
    - Clean players: max_yellow_cards=3, max_red_cards=0
    """
    try:
        return get_players(filters)
    except (ValueError, KeyError, TypeError) as e:
        return [{"error": str(e)}]
