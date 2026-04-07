"""Allow running as `python -m mcp_games`."""

import asyncio

from mcp_games import main

if __name__ == "__main__":
    asyncio.run(main())
