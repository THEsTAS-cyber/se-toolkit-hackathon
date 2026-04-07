"""Seed script — populate database with sample PS Store games."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.base import Base
from app.models.game import Game, PriceEntry

# Sample game data
SEED_GAMES = [
    {"name": "Elden Ring", "price": 39.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "God of War Ragnarök", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Spider-Man Remastered", "price": 29.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Cyberpunk 2077", "price": 19.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "The Last of Us Part I", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Ghost of Tsushima Director's Cut", "price": 34.99, "platforms": ["PS4", "PS5"], "region": "us", "currency": "USD"},
    {"name": "Horizon Forbidden West", "price": 39.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Resident Evil 4", "price": 29.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Final Fantasy XVI", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Baldur's Gate 3", "price": 59.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Stardew Valley", "price": 14.99, "platforms": ["PS4"], "region": "us", "currency": "USD"},
    {"name": "Hades", "price": 19.99, "platforms": ["PS4", "PS5"], "region": "us", "currency": "USD"},
    {"name": "Hollow Knight", "price": 14.99, "platforms": ["PS4"], "region": "us", "currency": "USD"},
    {"name": "It Takes Two", "price": 29.99, "platforms": ["PS4", "PS5"], "region": "us", "currency": "USD"},
    {"name": "Celeste", "price": 9.99, "platforms": ["PS4"], "region": "us", "currency": "USD"},
    {"name": "Dead Cells", "price": 24.99, "platforms": ["PS4"], "region": "us", "currency": "USD"},
    {"name": "Returnal", "price": 39.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Persona 5 Royal", "price": 29.99, "platforms": ["PS4", "PS5"], "region": "us", "currency": "USD"},
    {"name": "Gran Turismo 7", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "EA Sports FC 25", "price": 59.99, "platforms": ["PS4", "PS5"], "region": "us", "currency": "USD"},
    {"name": "Lies of P", "price": 34.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Astro Bot", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Silent Hill 2", "price": 49.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Helldivers 2", "price": 39.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
    {"name": "Metaphor: ReFantazio", "price": 59.99, "platforms": ["PS5"], "region": "us", "currency": "USD"},
]


async def seed_db(database_url: str) -> None:
    """Insert seed games if the table is empty."""
    engine = create_async_engine(database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        # Check if games already exist
        from sqlalchemy import select
        result = await session.execute(select(Game))
        existing = result.scalars().all()

        if existing:
            print(f"Database already has {len(existing)} games. Skipping seed.")
            return

        print("Seeding database with sample games...")
        now = datetime.now(timezone.utc)

        for g in SEED_GAMES:
            game = Game(
                name=g["name"],
                platforms=g["platforms"],
                store_url=f"https://store.playstation.com/{g['name'].lower().replace(' ', '-')}",
                created_at=now,
            )
            session.add(game)
            await session.flush()

            # Add price entry for the region
            price = PriceEntry(
                game_id=game.id,
                region=g["region"],
                currency=g["currency"],
                current_price=g["price"],
                original_price=g["price"] * 1.2,
                discount_percent=0,
                collected_at=now,
            )
            session.add(price)

        await session.commit()
        print(f"Seeded {len(SEED_GAMES)} games.")

    await engine.dispose()


if __name__ == "__main__":
    import sys
    db_url = sys.argv[1] if len(sys.argv) > 1 else "postgresql+asyncpg://postgres:postgres@localhost:5432/db-app"
    asyncio.run(seed_db(db_url))
