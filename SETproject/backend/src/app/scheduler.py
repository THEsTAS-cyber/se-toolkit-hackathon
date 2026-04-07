"""Background scheduler for price synchronization."""

import asyncio
import logging
from datetime import datetime

from app.database import async_session_factory
from app.services.price_sync import PriceSyncService
from app.settings import settings

logger = logging.getLogger(__name__)


class PriceSyncScheduler:
    def __init__(self) -> None:
        self.interval_hours = settings.pspricing_sync_interval_hours
        self.interval_seconds = self.interval_hours * 3600
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self.interval_seconds <= 0:
            logger.info("Price sync scheduler disabled")
            return
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Price sync scheduler started (every {self.interval_hours}h)")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Price sync scheduler stopped")

    async def _run_loop(self) -> None:
        while True:
            try:
                logger.info(f"Starting price sync at {datetime.utcnow().isoformat()}")
                await self._run_sync()
            except Exception as e:
                logger.error(f"Error in price sync cycle: {e}", exc_info=True)
            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    async def _run_sync(self) -> None:
        async with async_session_factory() as session:
            try:
                service = PriceSyncService(session)
                stats = await service.sync_all_regions()
                await session.commit()
                logger.info(f"Price sync completed: {stats}")
            except Exception as e:
                logger.error(f"Price sync failed: {e}", exc_info=True)
                await session.rollback()


scheduler = PriceSyncScheduler()
