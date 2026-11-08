"""Standalone FastMCP server for time, public web search, and weather."""

import os
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

mcp = FastMCP("Time, Search, and Weather")


@mcp.tool(
    name="get_current_datetime",
    description="Get the current date and time in an IANA timezone. Use UTC when no timezone is specified.",
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=False),
)
async def get_current_datetime(
    timezone: Annotated[str, Field(description="IANA timezone, such as Africa/Lagos.")] = "UTC",
) -> dict:
    try:
        now = datetime.now(ZoneInfo(timezone))
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("Unknown timezone. Use an IANA timezone such as Africa/Lagos.") from exc
    return {"datetime": now.isoformat(), "timezone": timezone}


@mcp.tool(
    name="fetch_web_search",
    description="Search the public web for current information. Returns up to five result titles, URLs, and snippets. Requires TAVILY_API_KEY.",
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
)
async def fetch_web_search(
    query: Annotated[str, Field(min_length=2, max_length=400, description="Specific public web search query.")],
) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY is required for web search.")
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"query": query, "search_depth": "basic", "max_results": 5},
        )
        response.raise_for_status()
    return [
        {"title": item.get("title"), "url": item.get("url"), "snippet": item.get("content")}
        for item in response.json().get("results", [])
    ]


@mcp.tool(
    name="get_current_weather",
    description="Get current weather for a city or place name. Returns the resolved location, observation time, temperature, humidity, wind speed, and WMO weather code from Open-Meteo.",
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
)
async def get_current_weather(
    location: Annotated[str, Field(min_length=2, max_length=100, description="City or place name, such as Lagos or London.")],
) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        geocode = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1},
        )
        geocode.raise_for_status()
        places = geocode.json().get("results") or []
        if not places:
            raise ValueError(f"No location found for {location!r}.")
        place = places[0]
        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            },
        )
        weather.raise_for_status()
    data = weather.json()
    return {
        "location": {"name": place["name"], "country": place.get("country")},
        "timezone": data.get("timezone"),
        "current": data["current"],
        "units": data.get("current_units"),
    }


@mcp.resource(
    "info://tool-guide",
    name="Tool guide",
    description="How to use this server's three tools and where their data comes from.",
    mime_type="text/plain",
)
def tool_guide() -> str:
    return (
        "get_current_datetime: current local date and time; timezone defaults to UTC.\n"
        "fetch_web_search: current public web results from Tavily; requires TAVILY_API_KEY.\n"
        "get_current_weather: current conditions for a place from Open-Meteo."
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host=os.getenv("MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("MCP_PORT", "8050")),
    )
