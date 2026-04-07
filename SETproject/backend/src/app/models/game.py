"""Game and pricing models."""

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Game(Base):
    """Game entity with PSPricing data."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # PSPricing identifiers
    ps_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True, index=True)
    sku: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    sku_suffix: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    concept_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Game info
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Metadata
    platforms: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    top_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Languages
    audio_languages: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    subtitle_languages: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )

    # Release info
    release_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # URLs
    store_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    modified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    price_entries: Mapped[list["PriceEntry"]] = relationship(
        "PriceEntry", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game {self.name} (title_id={self.title_id})>"


class PriceEntry(Base):
    """Price entry for a game in a specific region at a specific time."""

    __tablename__ = "price_entries"
    __table_args__ = (
        UniqueConstraint("game_id", "region", "collected_at", name="uq_price_entry"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Region & currency
    region: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    # Pricing data
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ps_plus_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Collection metadata
    collection: Mapped[str | None] = mapped_column(String(100), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="price_entries")

    def __repr__(self) -> str:
        return (
            f"<PriceEntry game_id={self.game_id} region={self.region} "
            f"price={self.current_price} {self.currency}>"
        )
