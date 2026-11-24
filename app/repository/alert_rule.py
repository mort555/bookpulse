from app.models.alert_rule import AlertRule
from app.repository.base import BaseRepository


class AlertRuleRepository(BaseRepository[AlertRule]):
    model = AlertRule

    async def get_by_user(self, user_id: int) -> list[AlertRule]:
        return await self.get_all_by(user_id=user_id)

    async def get_active_by_user(self, user_id: int) -> list[AlertRule]:
        return await self.get_all_by(user_id=user_id, is_active=True)
