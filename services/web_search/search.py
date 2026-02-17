from tavily import TavilyClient
from config import TAVILY_API_KEY
from services.web_search.config import PLAYER_SEARCH_CATEGORIES, TEAM_SEARCH_CATEGORIES, VIDEO_DOMAINS

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def search_player_context(player_name: str, team: str = None) -> dict:
    """
    Search web context about a player across 5 categories.
    Returns 5 results per category (25 total).
    """
    base_query = f"{player_name} {team}" if team else player_name

    context = {}
    for category, cat_config in PLAYER_SEARCH_CATEGORIES.items():
        search_params = {
            "query": f"{base_query} {cat_config['suffix']}",
            "max_results": 5,
        }

        if "topic" in cat_config:
            search_params["topic"] = cat_config["topic"]
        if "time_range" in cat_config:
            search_params["time_range"] = cat_config["time_range"]

        result = tavily_client.search(**search_params)
        context[category] = result.get("results", [])

    return {"player": player_name, "team": team, "context": context}


def search_team_context(team: str, league: str = None) -> dict:
    """
    Search web context about a team across 4 categories.
    Returns 3 results per category (12 total).
    """
    base_query = f"{team} {league}" if league else team

    context = {}
    for category, cat_config in TEAM_SEARCH_CATEGORIES.items():
        search_params = {
            "query": f"{base_query} {cat_config['suffix']}",
            "max_results": 3,
        }

        if "topic" in cat_config:
            search_params["topic"] = cat_config["topic"]
        if "time_range" in cat_config:
            search_params["time_range"] = cat_config["time_range"]

        result = tavily_client.search(**search_params)
        context[category] = result.get("results", [])

    return {"team": team, "league": league, "context": context}


def search_player_highlights(player_name: str, team: str = None, max_results: int = 5) -> dict:
    """Search highlight videos for a player from video platforms."""
    base_query = f"{player_name} {team}" if team else player_name

    result = tavily_client.search(
        query=f"{base_query} highlights goals skills",
        max_results=max_results,
        include_domains=VIDEO_DOMAINS,
    )

    return {
        "player": player_name,
        "team": team,
        "videos": [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "source": r.get("url", "").split("/")[2] if r.get("url") else "",
            }
            for r in result.get("results", [])
        ],
    }
