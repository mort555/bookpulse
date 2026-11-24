from app.models.alert import Alert
from app.repository.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    model = Alert

    async def get_pending(self) -> list[Alert]:
        return await self.get_all_by(notified_at=None)

    async def get_by_rule_and_product(
        self, rule_id: int, product_id: int
    ) -> list[Alert]:
        return await self.get_all_by(rule_id=rule_id, product_id=product_id)
