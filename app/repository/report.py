from app.models.report import Report
from app.repository.base import BaseRepository


class ReportRepository(BaseRepository[Report]):
    model = Report

    async def get_by_user(self, user_id: int) -> list[Report]:
        return await self.get_all_by(user_id=user_id)

    async def get_by_status(self, report_status: str) -> list[Report]:
        return await self.get_all_by(status=report_status)
