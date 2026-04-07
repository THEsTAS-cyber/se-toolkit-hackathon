# ProjectSET — PS Store Price Comparator

Compare PlayStation Store game prices across 67 regions worldwide — find the best deals and buy games cheaper.

## Demo

> 1. Game page — price comparison across all regions <img width="1910" height="1194" alt="Screenshot2" src="https://github.com/user-attachments/assets/2459554c-ba5f-4a64-adb8-6384e059101d" />
> 2. Wishlist / Favorites page <img width="1919" height="1199" alt="Screenshot1" src="https://github.com/user-attachments/assets/9b4e0b11-97f6-4d6d-a674-13c82dc304b3" />
> 3. Assistent dialog <img width="498" height="696" alt="ScreenshotAssistent" src="https://github.com/user-attachments/assets/f4e0ee94-4b9a-4fc3-802a-7c44c31d59e4" />



## Product Context

### End Users

- **Gamers from Russia and CIS countries** who use foreign PlayStation accounts (Turkey, Argentina, Poland, etc.) due to restrictions on the Russian PS Store.
- **Shoppers** looking for the region with the lowest price for a specific game.
- **Budget-conscious gamers** tracking discounts and sales.

### Problem

After the suspension of the PS Store in Russia, users are forced to create accounts in other countries. But finding where a game is cheapest is difficult: you need to visit each region's store individually, manually convert currencies, and track discounts. Price comparison becomes tedious and time-consuming.

### Our Solution

A unified catalog that **automatically collects prices** from 67 PS Store regions every 12 hours, converts them to rubles, and shows the **best deal** for each game. Users see: which country has the cheapest price, and can go directly to the purchase page in the desired region's PS Store.

> **Important:** We only parse **PlayStation games (PS4/PS5)**. Games from Epic Games Store, Steam, and other platforms are not displayed.

## Features

### Implemented (Version 1)

| Feature | Description |
|---------|-------------|
| **Price parsing from 67 PS Store regions** | Automatic data collection every 12 hours via PSPricing API |
| **PlayStation-only filter** | Only PS4/PS5 games shown, no Epic/Steam |
| **Catalog with covers and platforms** | PS5/PS4 badges, covers, discounts |
| **Price conversion to rubles** | Live exchange rates for 40+ currencies |
| **Best price highlight** | Green highlight on the region with the lowest ruble price |
| **All prices by region** | Expandable list with all 67 prices |
| **Direct PS Store links** | "🛒 PS Store" button goes to the purchase page in the selected region |
| **Search by title** | Instant catalog search |
| **Platform filter** | All / PS5 / PS4 |
| **Type filter** | All / Games / Bundles / DLC |
| **Sorting** | By best price / By name / By discount |
| **Registration & authentication** | JWT tokens, bcrypt password hashing |
| **Wishlist** | Save games to your personal profile |
| **AI assistant (nanobot)** | Chat widget in the corner for game-related questions |
| **Responsive design** | Mobile-friendly, fullscreen chat on mobile |

### Not Yet Implemented (Version 2)

| Feature | Priority |
|---------|----------|
| Price history chart | Medium |
| Price drop notifications for wishlist items | High |
| Export price list to CSV | Low |
| Side-by-side game comparison | Medium |
| DLC and add-ons display | Low |

## Usage

### Main Scenario

1. **Open the site** — `http://<your-VM-IP>:42002`
2. **Find a game** using search or browse the catalog.
3. **Check the best price** — highlighted in green on the game card.
4. **Expand "All prices"** — see the full list across all 67 regions with ruble conversion.
5. **Click "🛒 PS Store"** — go to the purchase page in the desired region.
6. **Add to wishlist** ❤️ — the game is saved to your profile.

### AI Assistant

Click the 💬 button in the bottom-right corner and ask, for example:
- *"Show me cheap games"*
- *"What RPG games are available?"*

## Deployment

### System Requirements

- **OS:** Ubuntu 24.04 LTS
- **RAM:** 4 GB minimum (8 GB recommended)
- **Disk:** 20 GB free space
- **Software:** Docker 26+, Docker Compose v2

### Step-by-Step Instructions

To use the AI assistant, you need to authorize your account in Qwen and have a `.qwen/oauth_creds.json` file.

```bash
# 1. Clone the repository
git clone https://github.com/THEsTAS-cyber/SETproject.git
cd SETproject

# 2. Create environment file
cp .env.docker.example .env
# Edit .env if needed (DB password, JWT secret, etc.)

# 3. Start all services
docker compose up -d --build

# 4. Wait for readiness (~30 seconds)
docker compose ps

# 5. Check backend health
curl http://localhost:42001/health

# 6. Verify price sync is running
docker compose logs backend --tail=30
```

### Services & Ports

| Service | Port | Description |
|---------|------|-------------|
| **Caddy (gateway)** | `42002` | Entry point, reverse proxy |
| **Backend API** | `42001` | FastAPI + PostgreSQL |
| **pgAdmin** | `42003` | Database management panel |
| **Nanobot (AI)** | `42006` | WebSocket chat assistant |
| **Qwen Code API** | `42005` | LLM proxy |

### Access Points

- **Frontend:** `http://<VM_IP>:42002`
- **pgAdmin:** `http://<VM_IP>:42003` (login: `admin@example.com` / `admin`)
- **Backend API:** `http://<VM_IP>:42001`

### Stopping

```bash
docker compose down
# To remove database data:
docker compose down -v
```

### Updating

```bash
git pull
docker compose up -d --build
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.14, FastAPI, SQLAlchemy (async) |
| **Database** | PostgreSQL 17 |
| **Frontend** | Next.js 15, React 19, TypeScript |
| **AI Agent** | Nanobot (WebSocket MCP) |
| **Gateway** | Caddy 2 |
| **Orchestration** | Docker Compose |
| **Package Manager** | uv |
| **Data Source** | PSPricing B2B API (67 regions) |
