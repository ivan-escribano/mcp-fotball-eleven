# Test HTTP client with API key
import asyncio
from fastmcp import Client

API_KEY = "sk_1a1681e1a6b9a9684ab7cebd8b4bb00a923401bcc291ddf2"


async def test():
    # API key in URL (like Tavily)
    url = f"http://localhost:8080/mcp?api_key={API_KEY}"

    async with Client(url) as client:
        # List tools
        tools = await client.list_tools()
        print("✅ Connected!")
        print(f"Tools: {[t.name for t in tools]}")

        # Search players with min 10 goals
        result = await client.call_tool("search_players", {
            "filters": {"min_goals": 10}
        })

        print("Players with 10+ goals:")
        print(result)

if __name__ == "__main__":
    asyncio.run(test())
