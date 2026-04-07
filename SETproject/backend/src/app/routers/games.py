"""Game CRUD router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db_session
from app.models.game import Game, PriceEntry
from app.schemas.game import GameCreate, GameOut, GamePriceComparison, inject_store_urls

router = APIRouter(prefix="/api/games", tags=["games"])


def _games_response(games: list[Game]) -> JSONResponse:
    """Convert games to dict and inject PS Store URLs."""
    data = []
    for g in games:
        gd = {
            "id": g.id,
            "ps_id": g.ps_id,
            "sku": g.sku,
            "sku_suffix": g.sku_suffix,
            "title_id": g.title_id,
            "concept_id": g.concept_id,
            "name": g.name,
            "description": g.description,
            "cover_url": g.cover_url,
            "platforms": g.platforms,
            "content_type": g.content_type,
            "top_category": g.top_category,
            "audio_languages": g.audio_languages,
            "subtitle_languages": g.subtitle_languages,
            "release_date": g.release_date.isoformat() if g.release_date else None,
            "store_url": g.store_url,
            "created_at": g.created_at.isoformat() if g.created_at else None,
            "modified_at": g.modified_at.isoformat() if g.modified_at else None,
            "last_synced_at": g.last_synced_at.isoformat() if g.last_synced_at else None,
            "price_entries": [
                {
                    "id": pe.id,
                    "region": pe.region,
                    "currency": pe.currency,
                    "current_price": pe.current_price,
                    "original_price": pe.original_price,
                    "discount_percent": pe.discount_percent,
                    "ps_plus_price": pe.ps_plus_price,
                    "collection": pe.collection,
                    "collected_at": pe.collected_at.isoformat() if pe.collected_at else None,
                }
                for pe in g.price_entries
            ],
        }
        data.append(inject_store_urls(gd))
    return JSONResponse(content=data)


@router.post("", response_model=GameOut, status_code=201)
async def create_game(
    data: GameCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Game:
    """Admin: add a new game."""
    game = Game(**data.model_dump())
    db.add(game)
    await db.flush()
    await db.refresh(game)
    return game


@router.get("", response_model=list[GameOut])
async def list_games(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=2000),
    ps_only: bool = Query(True, description="Show only PlayStation games"),
    db: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """List all games with their price entries."""
    stmt = select(Game).options(selectinload(Game.price_entries))
    if ps_only:
        # Filter: platforms array overlaps with ['PS5', 'PS4'] (raw SQL with explicit text[] cast)
        stmt = stmt.where(
            text("games.platforms && ARRAY[:p1, :p2]::text[]").bindparams(p1="PS5", p2="PS4")
        )
    stmt = stmt.order_by(Game.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return _games_response(list(result.scalars().all()))


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """Get available game categories with counts."""
    stmt = select(Game.content_type, Game.top_category).distinct()
    result = await db.execute(stmt)
    rows = result.all()

    categories = {}
    for content_type, top_category in rows:
        key = content_type or "unknown"
        if key not in categories:
            categories[key] = {"content_type": content_type, "top_categories": set()}
        if top_category:
            categories[key]["top_categories"].add(top_category)

    data = [
        {
            "content_type": v["content_type"],
            "top_categories": sorted(v["top_categories"]),
        }
        for v in categories.values()
    ]
    return JSONResponse(content=data)


# ── Specific paths MUST come before /{game_id} to avoid routing conflicts ──


@router.get("/search", response_model=list[GameOut])
async def search_games(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """Search games by name or description."""
    stmt = (
        select(Game)
        .options(selectinload(Game.price_entries))
        .where(
            or_(
                Game.name.ilike(f"%{q}%"),
                Game.description.ilike(f"%{q}%"),
            )
        )
        .order_by(Game.created_at.desc())
    )
    result = await db.execute(stmt)
    return _games_response(list(result.scalars().all()))


@router.get("/compare", response_model=list[GamePriceComparison])
async def compare_games_by_title(
    name: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """Find games by name and return their price comparisons."""
    stmt = (
        select(Game)
        .options(selectinload(Game.price_entries))
        .where(Game.name.ilike(f"%{name}%"))
        .order_by(Game.created_at.desc())
    )
    result = await db.execute(stmt)
    games = list(result.scalars().all())

    data = []
    for game in games:
        gd = {
            "game_id": game.id,
            "name": game.name,
            "title_id": game.title_id,
            "concept_id": game.concept_id,
            "sku_suffix": game.sku_suffix,
            "cover_url": game.cover_url,
            "price_entries": [
                {
                    "id": pe.id,
                    "region": pe.region,
                    "currency": pe.currency,
                    "current_price": pe.current_price,
                    "original_price": pe.original_price,
                    "discount_percent": pe.discount_percent,
                    "ps_plus_price": pe.ps_plus_price,
                    "collection": pe.collection,
                    "collected_at": pe.collected_at.isoformat() if pe.collected_at else None,
                }
                for pe in game.price_entries
            ],
        }
        # Rename price_entries to prices for comparison endpoint
        gd["prices"] = gd.pop("price_entries")
        inject_store_urls({"concept_id": gd["concept_id"], "price_entries": gd["prices"]})
        data.append(gd)
    return JSONResponse(content=data)


@router.get("/{game_id}", response_model=GameOut)
async def get_game(
    game_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> Game:
    """Get a single game by ID with price entries."""
    stmt = (
        select(Game)
        .options(selectinload(Game.price_entries))
        .where(Game.id == game_id)
    )
    result = await db.execute(stmt)
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/{game_id}/prices", response_model=GamePriceComparison)
async def get_game_price_comparison(
    game_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get price comparison for a game across all regions."""
    stmt = (
        select(Game)
        .options(selectinload(Game.price_entries))
        .where(Game.id == game_id)
    )
    result = await db.execute(stmt)
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return {
        "game_id": game.id,
        "name": game.name,
        "title_id": game.title_id,
        "cover_url": game.cover_url,
        "prices": game.price_entries,
    }


@router.delete("/{game_id}", status_code=204)
async def delete_game(
    game_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Admin: delete a game."""
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    await db.delete(game)
