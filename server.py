from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp import McpError
from mcp.types import ErrorData

from auth import validate_request

mcp = FastMCP("MCPEleven")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint for Azure (no auth required)."""
    return JSONResponse({"status": "healthy"})


class ApiKeyMiddleware(Middleware):
    """Validate API key from URL (?api_key=xxx) or header."""

    async def on_request(self, context: MiddlewareContext, call_next):
        request = get_http_request()

        if request and not validate_request(request):
            raise McpError(
                ErrorData(
                    code=-32001, message="Invalid or missing API key. Use ?api_key=sk_xxx")
            )

        return await call_next(context)


mcp.add_middleware(ApiKeyMiddleware())
