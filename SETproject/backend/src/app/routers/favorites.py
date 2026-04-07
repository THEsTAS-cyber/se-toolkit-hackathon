"""Favorites router — add/remove/list favorite games."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.deps import get_current_user
from app.database import get_db_session
from app.models.game import Game, PriceEntry
from app.models.user import User, UserFavoriteGame
from app.schemas.game import inject_store_urls

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


@router.get("", response_model=list[dict])
async def get_my_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> JSONResponse:
    """Get user's favorite games with full details."""
    stmt = (
        select(Game)
        .join(UserFavoriteGame, UserFavoriteGame.game_id == Game.id)
        .options(selectinload(Game.price_entries))
        .where(UserFavoriteGame.user_id == current_user.id)
        .order_by(UserFavoriteGame.added_at.desc())
    )
    result = await db.execute(stmt)
    games = list(result.scalars().all())

    data = []
    for g in games:
        gd = _game_to_dict(g)
        data.append(inject_store_urls(gd))
    return JSONResponse(content=data)


@router.post("/{game_id}", status_code=201)
async def add_favorite(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Add a game to favorites."""
    # Check game exists
    game = await db.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if already favorited
    stmt = select(UserFavoriteGame).where(
        UserFavoriteGame.user_id == current_user.id,
        UserFavoriteGame.game_id == game_id,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        return {"status": "already_favorited", "game_id": game_id}

    fav = UserFavoriteGame(user_id=current_user.id, game_id=game_id)
    db.add(fav)
    await db.flush()

    return {"status": "added", "game_id": game_id}


@router.delete("/{game_id}", status_code=204)
async def remove_favorite(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> None:
    """Remove a game from favorites."""
    stmt = delete(UserFavoriteGame).where(
        UserFavoriteGame.user_id == current_user.id,
        UserFavoriteGame.game_id == game_id,
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")


@router.get("/check/{game_id}")
async def check_favorite(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Check if a game is in user's favorites."""
    stmt = select(UserFavoriteGame).where(
        UserFavoriteGame.user_id == current_user.id,
        UserFavoriteGame.game_id == game_id,
    )
    result = await db.execute(stmt)
    exists = result.scalar_one_or_none() is not None
    return {"game_id": game_id, "is_favorite": exists}


def _game_to_dict(g: Game) -> dict:
    """Convert Game model to dict."""
    return {
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
