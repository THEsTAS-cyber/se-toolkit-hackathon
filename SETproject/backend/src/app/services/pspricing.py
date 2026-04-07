"""PSPricing API client."""

import logging
from datetime import datetime
from typing import Any

import httpx

from app.settings import settings

logger = logging.getLogger(__name__)


class PSPricingClient:
    """Client for PSPricing B2B API."""

    def __init__(self) -> None:
        self.base_url = settings.pspricing_base_url
        self.collection = settings.pspricing_collection
        self.regions = settings.pspricing_regions
        self.timeout = 30.0

    async def fetch_collection(self, region: str) -> dict[str, Any] | None:
        """Fetch game collection data for a specific region."""
        url = f"{self.base_url}?region={region}&collection={self.collection}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if data.get("meta", {}).get("demo"):
                    logger.debug(f"Using demo data for region '{region}'")

                logger.info(
                    f"Fetched {data.get('meta', {}).get('returned', 0)} games "
                    f"from region '{region}' "
                    f"(total available: {data.get('meta', {}).get('total_available', 0)})"
                )
                return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching region '{region}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching region '{region}': {e}")
            return None

    async def fetch_all_regions(self) -> list[dict[str, Any]]:
        """Fetch data from all configured regions."""
        results = []
        for region in self.regions:
            data = await self.fetch_collection(region)
            if data:
                results.append(data)
        return results

    @staticmethod
    def parse_game_data(item: dict[str, Any]) -> dict[str, Any]:
        """Parse raw API response into normalized game data."""
        languages = item.get("languages", {})
        pricing = item.get("pricing", {})

        release_date_str = item.get("release_date")
        release_date = None
        if release_date_str:
            try:
                release_date = datetime.fromisoformat(release_date_str)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse release date: {release_date_str}")

        return {
            "ps_id": item.get("id"),
            "sku": item.get("sku"),
            "sku_suffix": item.get("sku_suffix"),
            "title_id": item.get("title_id"),
            "concept_id": item.get("concept_id"),
            "name": item.get("name", ""),
            "cover_url": item.get("cover"),
            "platforms": item.get("platforms", []),
            "content_type": item.get("content_type"),
            "top_category": item.get("top_category"),
            "audio_languages": languages.get("audio", []),
            "subtitle_languages": languages.get("subtitles", []),
            "release_date": release_date,
            "modified_at": item.get("modified"),
            # Pricing data
            "region": pricing.get("region"),
            "currency": pricing.get("currency"),
            "current_price": pricing.get("current_price"),
            "original_price": pricing.get("original_price"),
            "discount_percent": pricing.get("discount_percent"),
            "ps_plus_price": pricing.get("ps_plus_price"),
        }
