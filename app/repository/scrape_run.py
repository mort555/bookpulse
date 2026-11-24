from app.models.scrape_run import ScrapeRun
from app.repository.base import BaseRepository


class ScrapeRunRepository(BaseRepository[ScrapeRun]):
    model = ScrapeRun

    async def get_by_status(self, run_status: str) -> list[ScrapeRun]:
        return await self.get_all_by(status=run_status)

    async def get_by_creator(self, user_id: int) -> list[ScrapeRun]:
        return await self.get_all_by(created_by=user_id)
