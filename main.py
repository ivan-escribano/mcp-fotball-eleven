from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp import McpError
from mcp.types import ErrorData

from db.database import get_players
from model import PlayerStatsFilters
from config import HOST, PORT
from auth import validate_request


mcp = FastMCP("ScoutFootballMCP")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint for Azure (no auth required)."""
    return JSONResponse({"status": "healthy"})


# FastMCP native middleware for API key validation
class ApiKeyMiddleware(Middleware):
    """Validate API key from URL (?api_key=xxx) or header."""

    async def on_request(self, context: MiddlewareContext, call_next):
        # Get HTTP request to check API key
        request = get_http_request()

        if request and not validate_request(request):
            raise McpError(
                ErrorData(
                    code=-32001, message="Invalid or missing API key. Use ?api_key=sk_xxx")
            )

        return await call_next(context)


# Add middleware to server
mcp.add_middleware(ApiKeyMiddleware())


@mcp.tool
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


if __name__ == "__main__":
    mcp.run(transport="http", host=HOST, port=PORT)
