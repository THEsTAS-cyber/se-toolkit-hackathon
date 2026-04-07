"""Pydantic schemas for game API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field


class PriceEntryOut(BaseModel):
    """Price entry output schema."""

    id: int
    region: str
    currency: str
    current_price: float | None
    original_price: float | None
    discount_percent: int | None
    ps_plus_price: float | None
    collection: str | None
    collected_at: datetime

    # PS Store link will be injected by router
    store_url: str | None = None

    model_config = {"from_attributes": True}


class GameCreate(BaseModel):
    """Schema for creating a game (admin)."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    cover_url: str | None = None
    platforms: list[str] = Field(default_factory=list)
    content_type: str | None = None
    top_category: str | None = None
    audio_languages: list[str] = Field(default_factory=list)
    subtitle_languages: list[str] = Field(default_factory=list)
    release_date: datetime | None = None
    store_url: str | None = None


class GameOut(BaseModel):
    """Game output schema."""

    id: int
    ps_id: int | None
    sku: str | None
    title_id: str | None
    concept_id: int | None
    name: str
    description: str | None
    cover_url: str | None
    platforms: list[str]
    content_type: str | None
    top_category: str | None
    audio_languages: list[str]
    subtitle_languages: list[str]
    release_date: datetime | None
    store_url: str | None
    created_at: datetime
    modified_at: datetime | None
    last_synced_at: datetime | None
    price_entries: list[PriceEntryOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class GamePriceComparison(BaseModel):
    """Schema for comparing game prices across regions."""

    game_id: int
    name: str
    title_id: str | None
    cover_url: str | None
    prices: list[PriceEntryOut]

    model_config = {"from_attributes": True}


# ── Helper: build PS Store URL ──

_PS_STORE_BASE = "https://store.playstation.com"

# Region code → PS Store locale prefix
_REGION_STORE_MAP: dict[str, str] = {
    # === PSPricing B2B API — все 70 регионов (region code → PS Store locale) ===
    "ae": "ar-AE", "ar": "es-AR", "at": "de-AT", "au": "en-AU",
    "be": "nl-BE", "bg": "bg-BG", "bh": "ar-BH", "bo": "es-BO", "br": "pt-BR", "ca": "en-CA",
    "ch": "de-CH", "cl": "es-CL", "cn": "zh-CN", "co": "es-CO", "cr": "es-CR", "cy": "el-CY",
    "cz": "cs-CZ", "de": "de-DE", "dk": "da-DK", "ec": "es-EC",
    "es": "es-ES", "fi": "fi-FI", "fr": "fr-FR", "gb": "en-GB", "gr": "el-GR", "gt": "es-GT",
    "hk": "zh-HK", "hn": "es-HN", "hr": "hr-HR", "hu": "hu-HU",
    "id": "id-ID", "ie": "en-IE", "il": "en-IL", "in": "en-IN", "is": "en-IS", "it": "it-IT",
    "jp": "ja-JP", "kr": "ko-KR", "kw": "ar-KW", "lb": "ar-LB",
    "lu": "de-LU", "mt": "en-MT", "mx": "es-MX", "my": "en-MY", "ni": "es-NI", "nl": "nl-NL",
    "no": "no-NO", "nz": "en-NZ", "om": "ar-OM", "pa": "es-PA",
    "pe": "es-PE", "pl": "pl-PL", "pt": "pt-PT", "py": "es-PY", "qa": "ar-QA", "ro": "ro-RO",
    "ru": "ru-RU", "sa": "ar-SA", "se": "sv-SE", "sg": "en-SG",
    "si": "sl-SI", "sk": "sk-SK", "sv": "es-SV", "th": "th-TH", "tr": "tr-TR", "tw": "zh-TW",
    "ua": "uk-UA", "us": "en-US", "uy": "es-UY", "za": "en-ZA",
}


def build_ps_store_url(region: str, concept_id: int | None) -> str | None:
    """Build a PS Store URL for a game in a given region."""
    if not concept_id:
        return None
    locale = _REGION_STORE_MAP.get(region, "en-US")
    return f"{_PS_STORE_BASE}/{locale}/concept/{concept_id}"


def inject_store_urls(game_data: dict[str, Any]) -> dict[str, Any]:
    """Inject store_url into each price_entry based on region + concept_id."""
    concept_id = game_data.get("concept_id")
    if "price_entries" in game_data and isinstance(game_data["price_entries"], list):
        for entry in game_data["price_entries"]:
            entry["store_url"] = build_ps_store_url(entry["region"], concept_id)
    return game_data
