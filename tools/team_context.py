from server import mcp
from services import search_team_context, TEAM_CONTEXT_PROMPT


@mcp.tool(description=TEAM_CONTEXT_PROMPT)
def get_team_context(team: str, league: str = None) -> dict:
    """
    Get tactical, market and performance context for a football team using real-time web search.

    Searches across 4 categories:
    - Formation, tactics and playing style
    - Coach profile and philosophy
    - Transfer targets and rumoured signings
    - League position and recent form

    Returns raw web results organized by category. The LLM decides
    what is relevant based on the user's question.

    Examples:
    - get_team_context("Real Madrid", "La Liga")
    - get_team_context("Manchester City")
    """
    try:
        return {
            "instructions": TEAM_CONTEXT_PROMPT,
            **search_team_context(team, league),
        }
    except Exception as e:
        return {"error": str(e)}
