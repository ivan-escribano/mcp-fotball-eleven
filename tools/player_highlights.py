from server import mcp
from services import search_player_highlights


@mcp.tool
def get_player_highlights(player_name: str, team: str = None, max_results: int = 5) -> dict:
    """
    Get highlight videos of a football player from YouTube, Instagram,
    TikTok, Facebook and Dailymotion.

    Returns a list of videos with title, URL and source platform.

    Examples:
    - get_player_highlights("Nico Paz", "Como")
    - get_player_highlights("Michael Olise", "Bayern Munich", max_results=10)
    """
    try:
        return search_player_highlights(player_name, team, max_results)
    except Exception as e:
        return {"error": str(e)}
