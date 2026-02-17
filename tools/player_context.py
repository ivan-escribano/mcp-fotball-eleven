from server import mcp
from services import search_player_context, PLAYER_CONTEXT_PROMPT


@mcp.tool(description=PLAYER_CONTEXT_PROMPT)
def get_player_context(player_name: str, team: str = None) -> dict:
    """
    Get deep scouting context for a football player using real-time web search.

    Searches across 5 categories:
    - Market value, salary, contract situation
    - Injury history and current fitness
    - Transfer history and career path
    - Awards, trophies and individual titles
    - Interviews, quotes and personality

    Returns raw web results organized by category. The LLM decides
    what is relevant based on the user's question.

    Examples:
    - get_player_context("Erling Haaland", "Manchester City")
    - get_player_context("Kylian Mbappé")
    """
    try:
        return {
            "instructions": PLAYER_CONTEXT_PROMPT,
            **search_player_context(player_name, team),
        }
    except Exception as e:
        return {"error": str(e)}
