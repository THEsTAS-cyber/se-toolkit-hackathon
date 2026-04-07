"""MCP server for game catalog queries."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

import urllib.request
import urllib.error
import os

BACKEND_URL = os.environ.get("NANOBOT_LMS_BACKEND_URL", "http://backend:8000")


def _fetch_json(path: str, params: dict | None = None) -> list[dict] | dict:
    url = f"{BACKEND_URL}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{qs}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _format_game(g: dict) -> str:
    """Format a game dict into a readable string."""
    name = g.get("name", "Unknown")
    entries = g.get("price_entries", [])

    # Find lowest price across all regions
    prices = [(e.get("currency", "?"), e.get("current_price", 0))
              for e in entries if e.get("current_price") is not None]
    if prices:
        best_currency, best_price = min(prices, key=lambda x: x[1])
        price_str = f"{best_price:.2f} {best_currency}"
    else:
        price_str = "N/A"

    platforms = ", ".join(g.get("platforms", []))
    return f"- {name} — {price_str} [{platforms}]"


# ── Tool schemas ──

class NoArgs(BaseModel):
    pass


class GenreQuery(BaseModel):
    genre: str = Field(description="Genre filter (deprecated, returns all games)")


class SearchQuery(BaseModel):
    q: str = Field(description="Search term for game title")


class CheapestQuery(BaseModel):
    limit: int = Field(default=5, ge=1, description="Number of cheapest games to return")


# ── Handlers ──

async def _list_games(_args: BaseModel) -> str:
    games = _fetch_json("/api/games")
    if not games:
        return "No games in catalog yet. The price sync may still be running."
    lines = [_format_game(g) for g in games[:20]]
    return f"Found {len(games)} games:\n" + "\n".join(lines)


async def _list_by_genre(args: BaseModel) -> str:
    # Genre filtering not implemented in new schema — return all
    games = _fetch_json("/api/games")
    if not games:
        return "No games in catalog."
    lines = [_format_game(g) for g in games[:20]]
    return f"Showing all games (genre filter not available):\n" + "\n".join(lines)


async def _search_games(args: BaseModel) -> str:
    games = _fetch_json("/api/games/search", params={"q": args.q})
    if not games:
        return f"No games found matching '{args.q}'."
    lines = [_format_game(g) for g in games[:10]]
    return f"Found {len(games)} game(s):\n" + "\n".join(lines)


async def _cheapest_games(args: BaseModel) -> str:
    games = _fetch_json("/api/games", params={"limit": 200})
    if not games:
        return "No games in catalog."

    # Sort by lowest price across all regions
    def get_lowest_price(g: dict) -> float:
        entries = g.get("price_entries", [])
        prices = [e.get("current_price", 999999)
                  for e in entries if e.get("current_price") is not None]
        return min(prices) if prices else 999999

    games.sort(key=get_lowest_price)
    lines = [_format_game(g) for g in games[:args.limit]]
    return f"Cheapest games:\n" + "\n".join(lines)


# ── Tool registry ──

from dataclasses import dataclass
from collections.abc import Awaitable, Callable
from mcp.types import Tool as MCPTool

ToolPayload = str
ToolHandler = Callable[[BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> MCPTool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return MCPTool(name=self.name, description=self.description, inputSchema=schema)


TOOL_SPECS = (
    ToolSpec(
        "list_games",
        "List all games from the catalog (up to 20). Returns name, lowest price, platforms.",
        NoArgs,
        _list_games,
    ),
    ToolSpec(
        "list_games_by_genre",
        "List games (genre filter deprecated).",
        GenreQuery,
        _list_by_genre,
    ),
    ToolSpec(
        "search_games",
        "Search games by title.",
        SearchQuery,
        _search_games,
    ),
    ToolSpec(
        "cheapest_games",
        "Get the cheapest games from the catalog by lowest price across all regions.",
        CheapestQuery,
        _cheapest_games,
    ),
)

TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


# ── Server ──

def create_server() -> Server:
    server = Server("game-catalog")

    @server.list_tools()
    async def list_tools() -> list[MCPTool]:
        return [spec.as_tool() for spec in TOOL_SPECS]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        spec = TOOLS_BY_NAME.get(name)
        if spec is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            args = spec.model.model_validate(arguments or {})
            result = await spec.handler(args)
            return [TextContent(type="text", text=result)]
        except urllib.error.URLError as exc:
            return [TextContent(type="text", text=f"Backend connection error: {exc}")]
        except Exception as exc:
            return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
