# Project Idea — PS Store Price Comparator

## Product Definition

**End-user:** Gamers from Russia and CIS countries who use foreign PlayStation accounts (Turkey, Argentina, Poland, etc.) due to PS Store restrictions in their region.

**Problem:** After the PS Store suspension in Russia, users must create accounts in other countries. Finding where a game is cheapest requires visiting each region's store individually, manually converting currencies, and tracking discounts. Price comparison is tedious and time-consuming.

**Product in one sentence:** A unified PS Store price comparison tool that automatically collects prices from 67 regions, converts them to rubles, and highlights the best deal for each game.

**Core feature:** Automated price collection from 67 PS Store regions with ruble conversion, best-price highlighting, and direct PS Store links for each region.

---

## Implementation Plan

### Version 1 — Manual Game Catalog

**Does one thing well:** Browse a manually curated game catalog with basic price info.

**What was missing:**
- Admins added games manually (no API integration)
- No user registration or authentication
- No wishlist/favorites
- Nanobot assistant had no MCP tools — couldn't query the catalog, only responded with generic answers
- No PS Store links to actual purchase pages

**Backend:**
- FastAPI REST API with basic game CRUD
- PostgreSQL with simple `games` table
- Price data entered manually by admins

**Frontend:**
- Simple game catalog page with static data
- No authentication UI
- No AI assistant widget

**Deliverable:** Basic catalog with manually entered games — functional but not automated.

---

### Version 2 — Automated PS Store Aggregator

**What changed:**
- Automated price import from PSPricing API (67 regions, every 12 hours)
- User registration & authentication (JWT tokens)
- Wishlist — save games to personal profile
- Nanobot assistant with MCP tools:
  - `list_games` — query the full catalog
  - `search_games` — find specific games
  - `list_games_by_genre` — filter by genre
  - `cheapest_games` — find budget deals
- Direct PS Store links for each region — users can go straight to the purchase page
- AI assistant works with real catalog data, not generic knowledge
- Caddy reverse proxy with WebSocket support for nanobot
- Responsive design with mobile-friendly chat

**Deliverable:** Fully automated PS Store price comparator with user accounts, wishlist, AI assistant that queries real data, and direct purchase links for 67 regions.

---

## Architecture

```
Version 2:

  [User Browser] ──→ [Caddy :42002] ──→ [Next.js User Panel]
                        │                    │
                        │              [Nanobot Widget]
                        │                    │
                        ├──────────────→ [Nanobot Gateway]
                        │                       │
                        │              [Qwen Code API (LLM)]
                        │                       │
                        │              [MCP: game-catalog tools]
                        │
                        ├──────────────→ [FastAPI Backend]
                        │                       │
                        │                  [PostgreSQL]
                        │                       │
                        │         [PSPricing API (ETL every 12h)]
                        │
                        └──────────────→ [pgAdmin (DB management)]
```
